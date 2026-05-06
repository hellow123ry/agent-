import { useEffect, useMemo, useState } from 'react'
import { ChatPanel } from '../components/chat/ChatPanel'
import { EvalPanel } from '../components/eval/EvalPanel'
import { KnowledgebasePanel } from '../components/knowledgebase/KnowledgebasePanel'
import { ReportsPanel } from '../components/reports/ReportsPanel'
import { StatePanel } from '../components/state/StatePanel'
import { TracePanel } from '../components/trace/TracePanel'
import {
  createSession,
  getEvalJob,
  getEvalResult,
  getKnowledgebase,
  getLatestReports,
  getReportHistory,
  resetSession,
  sendTurn,
  startEvalRun,
  updateHotels,
  updateRestaurants,
} from '../lib/api'
import type { ChatMessage, ChatState } from '../types/chat'
import type { EvalJobStatus, EvalResult, ReportArtifacts, ReportHistoryItem } from '../types/eval'
import type { HotelRecord, RestaurantRecord } from '../types/knowledgebase'
import type { TraceEvent } from '../types/trace'

const DATASET_PATH = 'evaluation/datasets/life_service_eval.json'

export function WorkbenchPage() {
  const [sessionId, setSessionId] = useState<string>()
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [state, setState] = useState<ChatState | null>(null)
  const [traces, setTraces] = useState<TraceEvent[]>([])
  const [chatBusy, setChatBusy] = useState(false)
  const [chatError, setChatError] = useState<string>()

  const [job, setJob] = useState<EvalJobStatus | null>(null)
  const [result, setResult] = useState<EvalResult | null>(null)
  const [evalBusy, setEvalBusy] = useState(false)
  const [evalError, setEvalError] = useState<string>()

  const [latestReports, setLatestReports] = useState<ReportArtifacts | null>(null)
  const [reportHistory, setReportHistory] = useState<ReportHistoryItem[]>([])
  const [restaurants, setRestaurants] = useState<RestaurantRecord[]>([])
  const [hotels, setHotels] = useState<HotelRecord[]>([])
  const [knowledgebaseBusy, setKnowledgebaseBusy] = useState(false)
  const [knowledgebaseError, setKnowledgebaseError] = useState<string>()

  async function bootstrapSession() {
    const session = await createSession()
    setSessionId(session.session_id)
    setMessages(session.messages)
    setState(session.state)
    setTraces([])
  }

  async function loadReports() {
    try {
      const [latest, history] = await Promise.all([getLatestReports(), getReportHistory()])
      setLatestReports(latest)
      setReportHistory(history)
    } catch (error) {
      console.error(error)
    }
  }

  async function loadKnowledgebase() {
    setKnowledgebaseBusy(true)
    setKnowledgebaseError(undefined)
    try {
      const payload = await getKnowledgebase()
      setRestaurants(payload.restaurants)
      setHotels(payload.hotels)
    } catch (error) {
      setKnowledgebaseError(error instanceof Error ? error.message : '加载知识库失败')
    } finally {
      setKnowledgebaseBusy(false)
    }
  }

  useEffect(() => {
    void bootstrapSession()
    void loadReports()
    void loadKnowledgebase()
  }, [])

  useEffect(() => {
    if (!job?.job_id || job.status === 'completed' || job.status === 'failed') {
      return
    }

    const timer = window.setInterval(async () => {
      try {
        const nextJob = await getEvalJob(job.job_id)
        setJob(nextJob)
        if (nextJob.status === 'completed') {
          const nextResult = await getEvalResult(job.job_id)
          setResult(nextResult)
          setEvalBusy(false)
          void loadReports()
        }
        if (nextJob.status === 'failed') {
          setEvalBusy(false)
          setEvalError(nextJob.error ?? '评测失败')
        }
      } catch (error) {
        setEvalBusy(false)
        setEvalError(error instanceof Error ? error.message : '获取评测状态失败')
      }
    }, 2000)

    return () => window.clearInterval(timer)
  }, [job?.job_id, job?.status])

  async function handleSend(message: string) {
    if (!sessionId) return
    setChatBusy(true)
    setChatError(undefined)
    try {
      const response = await sendTurn(sessionId, message)
      setMessages(response.messages)
      setState(response.state)
      setTraces(response.traces)
    } catch (error) {
      setChatError(error instanceof Error ? error.message : '发送消息失败')
    } finally {
      setChatBusy(false)
    }
  }

  async function handleReset() {
    if (!sessionId) return
    setChatBusy(true)
    setChatError(undefined)
    try {
      const response = await resetSession(sessionId)
      setMessages(response.messages)
      setState(response.state)
      setTraces([])
    } catch (error) {
      setChatError(error instanceof Error ? error.message : '重置会话失败')
    } finally {
      setChatBusy(false)
    }
  }

  async function handleRunEval() {
    setEvalBusy(true)
    setEvalError(undefined)
    setResult(null)
    try {
      const nextJob = await startEvalRun(DATASET_PATH)
      setJob({ job_id: nextJob.job_id, status: nextJob.status, partial_metrics: {} })
    } catch (error) {
      setEvalBusy(false)
      setEvalError(error instanceof Error ? error.message : '启动评测失败')
    }
  }

  async function handleSaveRestaurants(nextRestaurants: RestaurantRecord[]) {
    setKnowledgebaseError(undefined)
    const payload = await updateRestaurants(nextRestaurants)
    setRestaurants(payload.restaurants)
    setHotels(payload.hotels)
  }

  async function handleSaveHotels(nextHotels: HotelRecord[]) {
    setKnowledgebaseError(undefined)
    const payload = await updateHotels(nextHotels)
    setRestaurants(payload.restaurants)
    setHotels(payload.hotels)
  }

  const title = useMemo(() => '生活服务 Multi-Agent Workbench', [])

  return (
    <main className="workbench-shell">
      <header className="workbench-header">
        <div className="hero-copy">
          <span className="hero-badge">Local Visual Workbench</span>
          <h1>{title}</h1>
          <p>对话调试、过程追踪、评测结果与报告文件统一展示。</p>
        </div>
        <div className="hero-summary">
          <div className="summary-chip">
            <span>Session</span>
            <strong>{sessionId ?? '初始化中'}</strong>
          </div>
          <div className="summary-chip">
            <span>Active Task</span>
            <strong>{state?.active_task || 'none'}</strong>
          </div>
          <div className="summary-chip">
            <span>Eval Status</span>
            <strong>{job?.status ?? 'idle'}</strong>
          </div>
        </div>
      </header>
      <section className="workbench-grid">
        <div className="left-column">
          <ChatPanel
            sessionId={sessionId}
            messages={messages}
            busy={chatBusy}
            error={chatError}
            onSend={handleSend}
            onReset={handleReset}
          />
          <KnowledgebasePanel
            restaurants={restaurants}
            hotels={hotels}
            busy={knowledgebaseBusy}
            error={knowledgebaseError}
            onReload={loadKnowledgebase}
            onSaveRestaurants={handleSaveRestaurants}
            onSaveHotels={handleSaveHotels}
          />
        </div>
        <div className="middle-column">
          <TracePanel traces={traces} />
          <StatePanel state={state} />
        </div>
        <div className="right-column">
          <EvalPanel job={job} result={result} busy={evalBusy} error={evalError} onRun={handleRunEval} />
          <ReportsPanel latest={latestReports} history={reportHistory} />
        </div>
      </section>
    </main>
  )
}
