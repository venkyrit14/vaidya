export function CommandHeader() {
  return (
    <header className="flex shrink-0 items-center justify-between border-b border-hairline px-6 py-4">
      <div>
        <h2 className="m-0 text-[18px] font-semibold text-primary">
          Command Center
        </h2>
        <p className="mt-0.5 mb-0 text-[13px] text-secondary">
          Revenue recovery operations
        </p>
      </div>

      <div className="flex items-center gap-3">
        <div
          className="flex items-center gap-2 rounded-[4px] border border-hairline bg-panel px-3 py-1.5 text-[12px] font-medium text-primary"
          role="status"
          aria-label="Feed status: live"
        >
          <span
            className="live-indicator h-2 w-2 shrink-0 rounded-full bg-agent"
            aria-hidden="true"
          />
          <span>Live</span>
        </div>
      </div>
    </header>
  )
}
