import request from "@/utils/request";

/* ── 学生信息 ────────────────────────────────────────── */

export interface StudentRecord {
  id: number;
  student_no: string;
  name: string;
  gender: number;
  class_name: string;
  major: string;
  college: string;
  phone: string;
  email: string;
  enrollment_year: number | null;
  status: number;
  remark: string;
  create_time: string;
  update_time: string;
}

export interface StudentListParams {
  page?: number;
  pageSize?: number;
  name?: string;
  student_no?: string;
  class_name?: string;
  status?: number;
}

export function getStudentList(params: StudentListParams): Promise<{ records: StudentRecord[]; total: number }> {
  return request.get("/student/info", { params });
}

export function createStudent(data: Partial<StudentRecord>): Promise<StudentRecord> {
  return request.post("/student/info", data);
}

export function updateStudent(id: number, data: Partial<StudentRecord>): Promise<StudentRecord> {
  return request.put(`/student/info/${id}`, data);
}

export function deleteStudent(id: number): Promise<void> {
  return request.delete(`/student/info/${id}`);
}

export function batchDeleteStudents(ids: number[]): Promise<void> {
  return request.delete("/student/info/batch", { data: { ids } });
}

export function updateStudentStatus(id: number, status: number): Promise<void> {
  return request.put(`/student/info/${id}/status`, { status });
}

export function exportStudents(): Promise<Blob> {
  return request.get("/student/info/export", { responseType: "blob" });
}

/* ── 学生成绩 ────────────────────────────────────────── */

export interface ScoreRecord {
  id: number;
  student: number;
  student_name: string;
  student_no: string;
  course_name: string;
  score: number;
  semester: string;
  credit: number | null;
  remark: string;
  create_time: string;
  update_time: string;
}

export interface ScoreListParams {
  page?: number;
  pageSize?: number;
  student_id?: number;
  course_name?: string;
  semester?: string;
}

export function getScoreList(params: ScoreListParams): Promise<{ records: ScoreRecord[]; total: number }> {
  return request.get("/student/score", { params });
}

export function createScore(data: { student: number; course_name: string; score: number; semester: string; credit?: number | null; remark?: string }): Promise<ScoreRecord> {
  return request.post("/student/score", data);
}

export function updateScore(id: number, data: Partial<{ student: number; course_name: string; score: number; semester: string; credit: number | null; remark: string }>): Promise<ScoreRecord> {
  return request.put(`/student/score/${id}`, data);
}

export function deleteScore(id: number): Promise<void> {
  return request.delete(`/student/score/${id}`);
}

export function batchDeleteScores(ids: number[]): Promise<void> {
  return request.delete("/student/score/batch", { data: { ids } });
}

export function exportScores(): Promise<Blob> {
  return request.get("/student/score/export", { responseType: "blob" });
}
