type KpiBlockProps = {
  label: string
  value: string
}

export function KpiBlock({ label, value }: KpiBlockProps) {
  return (
    <div>
      <p className="m-0 text-[12px] leading-4 text-secondary">{label}</p>
      <p className="font-data m-0 mt-2 text-[32px] font-semibold leading-none text-primary">
        {value}
      </p>
    </div>
  )
}
