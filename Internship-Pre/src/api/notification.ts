import request from "@/utils/request";

export interface NotificationRecord {
  id: number;
  title: string;
  content: string;
  notification_type: number;
  type_display: string;
  is_read: boolean;
  extra_data: any;
  create_time: string;
  read_time: string | null;
}

export interface NotificationListParams {
  page?: number;
  pageSize?: number;
  is_read?: string;
  type?: number;
}

export function getNotificationList(params: NotificationListParams): Promise<{ records: NotificationRecord[]; total: number }> {
  return request.get("/notification/", { params });
}

export function getNotificationDetail(id: number): Promise<NotificationRecord> {
  return request.get(`/notification/${id}`);
}

export function deleteNotification(id: number): Promise<void> {
  return request.delete(`/notification/${id}`);
}

export function markNotificationRead(id: number): Promise<void> {
  return request.put(`/notification/${id}/read`);
}

export function markAllNotificationsRead(): Promise<{ count: number }> {
  return request.put("/notification/read-all");
}

export function getUnreadCount(): Promise<{ count: number }> {
  return request.get("/notification/unread-count");
}

export function clearReadNotifications(): Promise<{ count: number }> {
  return request.delete("/notification/clear-read");
}
