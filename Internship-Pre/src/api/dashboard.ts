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
  today_login_count?: number;
  dept_distribution?: Array<{ dept_name: string; user_count: number }>;
  login_trend?: Array<{ date: string; count: number }>;
}

export function getDashboardStats(): Promise<DashboardStats> {
  return request.get("/dashboard/stats/");
}