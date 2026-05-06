import type { ChatSession, ChatTurnResponse } from '../types/chat'
import type { EvalJobStatus, EvalResult, ReportArtifacts, ReportHistoryItem } from '../types/eval'
import type { HotelRecord, KnowledgebaseEnvelope, RestaurantRecord } from '../types/knowledgebase'

const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL as string | undefined) ?? 'http://127.0.0.1:8000'

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: { 'Content-Type': 'application/json', ...(init?.headers ?? {}) },
    ...init,
  })

  if (!response.ok) {
    const text = await response.text()
    throw new Error(text || `Request failed: ${response.status}`)
  }

  return response.json() as Promise<T>
}

export function createSession() {
  return request<ChatSession>('/api/chat/session', { method: 'POST' })
}

export function getSession(sessionId: string) {
  return request<ChatSession>(`/api/chat/session/${sessionId}`)
}

export function resetSession(sessionId: string) {
  return request<ChatSession>(`/api/chat/session/${sessionId}`, { method: 'DELETE' })
}

export function sendTurn(sessionId: string, message: string) {
  return request<ChatTurnResponse>(`/api/chat/session/${sessionId}/turn`, {
    method: 'POST',
    body: JSON.stringify({ message }),
  })
}

export function startEvalRun(datasetPath: string) {
  return request<{ job_id: string; status: string }>('/api/eval/run', {
    method: 'POST',
    body: JSON.stringify({ dataset_path: datasetPath }),
  })
}

export function getEvalJob(jobId: string) {
  return request<EvalJobStatus>(`/api/eval/jobs/${jobId}`)
}

export function getEvalResult(jobId: string) {
  return request<EvalResult>(`/api/eval/jobs/${jobId}/result`)
}

export function getLatestReports() {
  return request<ReportArtifacts>('/api/reports/latest')
}

export async function getReportHistory() {
  const response = await request<{ items: ReportHistoryItem[] }>('/api/reports/history')
  return response.items
}

export function getReportFileUrl(path?: string) {
  if (!path) return '#'
  const relativePath = path.startsWith('evaluation/results/')
    ? path.replace('evaluation/results/', '')
    : path
  return `${API_BASE_URL}/api/reports/file?path=${encodeURIComponent(relativePath)}`
}

export async function getKnowledgebase() {
  const response = await request<KnowledgebaseEnvelope>('/api/knowledgebase')
  if (!response.ok || !response.data) {
    throw new Error(response.error?.message ?? '获取知识库失败')
  }
  return response.data
}

export async function updateRestaurants(restaurants: RestaurantRecord[]) {
  const response = await request<KnowledgebaseEnvelope>('/api/knowledgebase/restaurants', {
    method: 'PUT',
    body: JSON.stringify({ restaurants }),
  })
  if (!response.ok || !response.data) {
    throw new Error(response.error?.message ?? '保存餐厅知识库失败')
  }
  return response.data
}

export async function updateHotels(hotels: HotelRecord[]) {
  const response = await request<KnowledgebaseEnvelope>('/api/knowledgebase/hotels', {
    method: 'PUT',
    body: JSON.stringify({ hotels }),
  })
  if (!response.ok || !response.data) {
    throw new Error(response.error?.message ?? '保存酒店知识库失败')
  }
  return response.data
}
