import { apiGet, apiPost } from './client.ts'
import type {
  BatchEventsResponse,
  BatchSummary,
  CaseDetailsResponse,
  PaginatedRecordsResponse,
  PolicyConfig,
  ProcessBatchRequest,
  ProcessBatchResponse,
  RecoveryRequest,
  RecoveryResponse,
  RecoverySummaryResponse,
  SystemStatus,
} from '../types/recovery.ts'

export function analyzeRecovery(
  request: RecoveryRequest,
): Promise<RecoveryResponse> {
  return apiPost<RecoveryResponse, RecoveryRequest>(
    '/api/recovery/analyze',
    request,
  )
}

export function getRecoverySummary(): Promise<RecoverySummaryResponse> {
  return apiGet<RecoverySummaryResponse>('/api/recovery/summary')
}

export type RecordQueryParams = {
  search?: string
  event_type?: string
  outcome?: string
  action?: string
  requires_human?: boolean
  page?: number
  limit?: number
}

export function getRecoveryRecords(
  params?: RecordQueryParams,
): Promise<PaginatedRecordsResponse> {
  return apiGet<PaginatedRecordsResponse>('/api/recovery/records', params)
}

export function getRecordById(caseId: string): Promise<CaseDetailsResponse> {
  return apiGet<CaseDetailsResponse>(`/api/recovery/records/${encodeURIComponent(caseId)}`)
}

export function getBatches(): Promise<BatchSummary[]> {
  return apiGet<BatchSummary[]>('/api/recovery/batches')
}

export type BatchEventsQueryParams = {
  search?: string
  page?: number
  limit?: number
}

export function getBatchEvents(
  batchId: string,
  params?: BatchEventsQueryParams,
): Promise<BatchEventsResponse> {
  return apiGet<BatchEventsResponse>(
    `/api/recovery/batches/${encodeURIComponent(batchId)}/events`,
    params,
  )
}

export function processBatch(
  request: ProcessBatchRequest,
): Promise<ProcessBatchResponse> {
  return apiPost<ProcessBatchResponse, ProcessBatchRequest>(
    '/api/recovery/process-batch',
    request,
  )
}

export function getPolicies(): Promise<PolicyConfig> {
  return apiGet<PolicyConfig>('/api/recovery/policies')
}

export function getSystemStatus(): Promise<SystemStatus> {
  return apiGet<SystemStatus>('/api/recovery/system-status')
}
