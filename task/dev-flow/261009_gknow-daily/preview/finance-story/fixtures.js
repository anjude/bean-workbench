import { useFinanceStoryPresentation as useRealQuiz } from '@/composables/useFinanceStoryPresentation'

// 定位仅用于浏览器审稿；生产页面不读取 URL，也不暴露状态。
export function useFinanceStoryPresentation() {
  const quiz = useRealQuiz()
  const params = new URLSearchParams(location.search)
  const target = params.get('screen') || 'cover'
  if (target !== 'cover') {
    quiz.start(20261023)
    for (let guard = 0; guard < quiz.totalQuestions; guard++) {
      if (quiz.item.value?.id === target || quiz.phase.value === 'result') break
      quiz.record(target === 'empty' ? null : quiz.item.value.options['ABCD'.indexOf((params.get('choices') || 'ACACACAABDAC')[guard])]?.id || null)
      quiz.advance()
    }
    if (params.has('answer') && quiz.item.value && quiz.phase.value === 'question') {
      const index = 'ABCD'.indexOf(params.get('answer'))
      if (index >= 0) quiz.record(quiz.item.value.options[index].id)
    }
  }
  window.__financePreview = quiz
  return quiz
}
