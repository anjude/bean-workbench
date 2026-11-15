package main

import (
	"bytes"
	"encoding/json"
	"errors"
	"flag"
	"fmt"
	"io"
	"mime/multipart"
	"net/http"
	"net/url"
	"os"
	"path/filepath"
	"strings"
	"time"

	"github.com/golang-jwt/jwt/v4"
	"github.com/spf13/viper"
)

const maxBodyBytes = 4 << 20

// Keep the public JWT wire shape local so this standalone helper can live
// outside the backend module's internal package boundary.
type apiClaims struct {
	jwt.RegisteredClaims
	Openid    *string
	Admin     *int8
	AppId     *string
	LoginType *int8
}

type appConfig struct {
	App struct {
		JWTKey     string `mapstructure:"jwt_key"`
		GknowAppID string `mapstructure:"gknow_app_id"`
	} `mapstructure:"app"`
}

func main() {
	env := flag.String("env", "", "target environment: test or live")
	admin := flag.Bool("admin", false, "sign an admin claim; only use for an explicitly authorized admin API operation")
	openidFile := flag.String("openid-file", "", "local file containing one OpenID line")
	method := flag.String("method", "GET", "HTTP method: GET or POST")
	apiPath := flag.String("path", "", "relative API path under /api/so/")
	bodyFile := flag.String("body-file", "", "optional JSON request body file")
	uploadFile := flag.String("upload-file", "", "optional local image to upload as multipart field 'file'")
	configDir := flag.String("config-dir", "configs", "backend config directory, relative to current working directory")
	ttlMinutes := flag.Int("ttl-minutes", 15, "JWT lifetime in minutes (1-60)")
	flag.Parse()

	if err := run(*env, *admin, *openidFile, *method, *apiPath, *bodyFile, *uploadFile, *configDir, *ttlMinutes); err != nil {
		fmt.Fprintln(os.Stderr, "backend API request failed:", err)
		os.Exit(1)
	}
}

func run(env string, admin bool, openidFile, method, apiPath, bodyFile, uploadFile, configDir string, ttlMinutes int) error {
	if env != "test" && env != "live" {
		return errors.New("-env must be explicitly set to test or live")
	}
	if ttlMinutes < 1 || ttlMinutes > 60 {
		return errors.New("JWT lifetime must be between 1 and 60 minutes")
	}
	method = strings.ToUpper(method)
	if method != http.MethodGet && method != http.MethodPost {
		return errors.New("only GET and POST are supported")
	}
	parsedPath, err := url.ParseRequestURI(apiPath)
	if err != nil || parsedPath.IsAbs() || parsedPath.Host != "" || !strings.HasPrefix(parsedPath.Path, "/api/so/") {
		return errors.New("-path must be a relative path under /api/so/")
	}
	for _, segment := range strings.Split(parsedPath.Path, "/") {
		if segment == ".." {
			return errors.New("API path may not traverse directories")
		}
	}
	if openidFile == "" {
		return errors.New("-openid-file is required")
	}
	if bodyFile != "" && uploadFile != "" {
		return errors.New("-body-file and -upload-file cannot be used together")
	}
	openidBytes, err := os.ReadFile(openidFile)
	if err != nil {
		return fmt.Errorf("cannot read local OpenID file: %w", err)
	}
	openid := strings.TrimSpace(string(openidBytes))
	if openid == "" || strings.ContainsAny(openid, "\r\n") {
		return errors.New("OpenID file must contain exactly one non-empty line")
	}

	cfg, err := loadConfig(configDir, env)
	if err != nil {
		return err
	}
	if cfg.App.JWTKey == "" || cfg.App.GknowAppID == "" {
		return errors.New("environment config is missing app.jwt_key or app.gknow_app_id")
	}
	adminClaim := int8(0)
	if admin {
		adminClaim = 1
	}
	loginType := int8(1)
	claims := apiClaims{
		RegisteredClaims: jwt.RegisteredClaims{
			Issuer:    "so",
			ExpiresAt: jwt.NewNumericDate(time.Now().Add(time.Duration(ttlMinutes) * time.Minute)),
		},
		Openid:    &openid,
		Admin:     &adminClaim,
		AppId:     &cfg.App.GknowAppID,
		LoginType: &loginType,
	}
	token, err := jwt.NewWithClaims(jwt.SigningMethodHS256, claims).SignedString([]byte(cfg.App.JWTKey))
	if err != nil {
		return errors.New("could not sign environment JWT")
	}

	var body io.Reader
	contentType := ""
	if uploadFile != "" {
		if method != http.MethodPost {
			return errors.New("-upload-file is only supported for POST")
		}
		file, err := os.Open(filepath.Clean(uploadFile))
		if err != nil {
			return fmt.Errorf("cannot open upload file: %w", err)
		}
		defer file.Close()
		info, err := file.Stat()
		if err != nil || info.Size() == 0 || info.Size() > maxBodyBytes {
			return errors.New("upload file must be between 1 byte and 4 MiB")
		}
		var payload bytes.Buffer
		writer := multipart.NewWriter(&payload)
		part, err := writer.CreateFormFile("file", filepath.Base(uploadFile))
		if err != nil {
			return errors.New("could not prepare multipart upload")
		}
		if _, err := io.Copy(part, file); err != nil {
			return errors.New("could not read upload file")
		}
		if err := writer.Close(); err != nil {
			return errors.New("could not finalize multipart upload")
		}
		body = &payload
		contentType = writer.FormDataContentType()
	}
	if bodyFile != "" {
		if method == http.MethodGet {
			return errors.New("-body-file is only supported for POST")
		}
		data, err := os.ReadFile(filepath.Clean(bodyFile))
		if err != nil {
			return fmt.Errorf("cannot read request body: %w", err)
		}
		if len(data) > maxBodyBytes {
			return errors.New("request body exceeds 4 MiB")
		}
		if !json.Valid(data) {
			return errors.New("request body is not valid JSON")
		}
		body = strings.NewReader(string(data))
		contentType = "application/json"
	}

	baseURL := "https://api.beanflow.top"
	if env == "test" {
		baseURL += ":8080"
	}
	req, err := http.NewRequest(method, baseURL+apiPath, body)
	if err != nil {
		return errors.New("could not construct API request")
	}
	req.Header.Set("Authorization", "Bearer "+token)
	if contentType != "" {
		req.Header.Set("Content-Type", contentType)
	}
	client := &http.Client{
		Timeout: 25 * time.Second,
		CheckRedirect: func(*http.Request, []*http.Request) error {
			return http.ErrUseLastResponse
		},
	}
	resp, err := client.Do(req)
	if err != nil {
		return fmt.Errorf("request did not complete: %w", err)
	}
	defer resp.Body.Close()
	respBody, err := io.ReadAll(io.LimitReader(resp.Body, maxBodyBytes+1))
	if err != nil {
		return errors.New("could not read API response")
	}
	if len(respBody) > maxBodyBytes {
		return errors.New("API response exceeds 4 MiB")
	}
	output := map[string]any{"environment": env, "http_status": resp.StatusCode}
	if len(respBody) > 0 {
		var value any
		if json.Unmarshal(respBody, &value) == nil {
			output["response"] = redact(value)
		} else {
			output["response_text"] = "[non-JSON response omitted]"
		}
	}
	encoded, err := json.MarshalIndent(output, "", "  ")
	if err != nil {
		return errors.New("could not encode redacted API response")
	}
	fmt.Println(string(encoded))
	if resp.StatusCode >= 400 {
		return fmt.Errorf("HTTP status %d", resp.StatusCode)
	}
	if value, ok := output["response"].(map[string]any); ok {
		if code, ok := value["err_code"].(float64); ok && code != 0 {
			return fmt.Errorf("API returned business error code %v", code)
		}
	}
	return nil
}

func loadConfig(configDir, env string) (*appConfig, error) {
	base := filepath.Join(configDir, "config.yaml")
	v := viper.New()
	v.SetConfigType("yaml")
	v.SetConfigFile(base)
	if err := v.ReadInConfig(); err != nil {
		return nil, errors.New("could not read base backend config")
	}
	if env == "test" {
		v.SetConfigFile(filepath.Join(configDir, "config.test.yaml"))
		if err := v.MergeInConfig(); err != nil {
			return nil, errors.New("could not merge test backend config")
		}
	}
	var cfg appConfig
	if err := v.Unmarshal(&cfg); err != nil {
		return nil, errors.New("could not parse backend config")
	}
	return &cfg, nil
}

func redact(value any) any {
	switch typed := value.(type) {
	case map[string]any:
		result := make(map[string]any, len(typed))
		for key, child := range typed {
			lower := strings.ToLower(key)
			if strings.Contains(lower, "token") || strings.Contains(lower, "secret") || strings.Contains(lower, "password") || strings.Contains(lower, "authorization") || lower == "jwt" {
				result[key] = "[redacted]"
			} else {
				result[key] = redact(child)
			}
		}
		return result
	case []any:
		result := make([]any, len(typed))
		for index, child := range typed {
			result[index] = redact(child)
		}
		return result
	default:
		return value
	}
}
