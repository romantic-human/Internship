/**
 * 日期格式化工具函数
 * 统一项目中时间显示格式
 */

/**
 * 格式化日期
 * @param date - 日期字符串、Date 对象或时间戳
 * @param format - 格式模板，默认 'YYYY-MM-DD HH:mm:ss'
 * @example formatDate('2024-01-15T10:30:00') → '2024-01-15 10:30:00'
 * @example formatDate(new Date(), 'YYYY-MM-DD') → '2024-01-15'
 */
export function formatDate(
  date: string | Date | number | null | undefined,
  format: string = "YYYY-MM-DD HH:mm:ss"
): string {
  if (!date) return "-";

  let d: Date;
  if (typeof date === "string") {
    d = new Date(date);
  } else if (typeof date === "number") {
    d = new Date(date);
  } else {
    d = date;
  }

  if (isNaN(d.getTime())) return "-";

  const pad = (n: number): string => n.toString().padStart(2, "0");

  const tokens: Record<string, string> = {
    YYYY: d.getFullYear().toString(),
    MM: pad(d.getMonth() + 1),
    DD: pad(d.getDate()),
    HH: pad(d.getHours()),
    mm: pad(d.getMinutes()),
    ss: pad(d.getSeconds()),
  };

  return format.replace(/YYYY|MM|DD|HH|mm|ss/g, (match) => tokens[match] || match);
}

/**
 * 格式化为日期（不含时间）
 */
export function formatDateOnly(date: string | Date | number | null | undefined): string {
  return formatDate(date, "YYYY-MM-DD");
}

/**
 * 格式化为时间（不含日期）
 */
export function formatTimeOnly(date: string | Date | number | null | undefined): string {
  return formatDate(date, "HH:mm:ss");
}

/**
 * 相对时间（多久前）
 * @example timeAgo('2024-01-15T10:30:00') → '3小时前'
 */
export function timeAgo(date: string | Date | number): string {
  const d = typeof date === "string" || typeof date === "number" ? new Date(date) : date;
  if (isNaN(d.getTime())) return "-";

  const now = Date.now();
  const diff = now - d.getTime();
  const seconds = Math.floor(diff / 1000);
  const minutes = Math.floor(seconds / 60);
  const hours = Math.floor(minutes / 60);
  const days = Math.floor(hours / 24);
  const months = Math.floor(days / 30);

  if (seconds < 60) return "刚刚";
  if (minutes < 60) return `${minutes}分钟前`;
  if (hours < 24) return `${hours}小时前`;
  if (days < 30) return `${days}天前`;
  if (months < 12) return `${months}个月前`;
  return formatDate(d, "YYYY-MM-DD");
}
