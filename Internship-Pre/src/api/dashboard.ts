import request from "@/utils/request";

export interface DashboardStats {
  user_count: number;
  role_count: number;
  menu_count: number;
  permission_count: number;
  department_count: number;
  log_today: number;
  log_week: number;
  log_month: number;
  recent_logs: {
    username: string;
    module: string;
    operation: string;
    ip: string;
    execution_time: number;
    create_time: string;
  }[];
}

export function getDashboardStats(): Promise<DashboardStats> {
  return request.get("/dashboard/stats/");
}

export interface TrendData {
  log_trend: { date: string; count: number }[];
  role_distribution: { role_name: string; user_count: number }[];
}

export function getDashboardTrend(): Promise<TrendData> {
  return request.get("/dashboard/stats/trend");
}