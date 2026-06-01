import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class InterviewService {
  private apiUrl = 'http://localhost:8000';

  constructor(private http: HttpClient) {}

  startInterview(file: File, role: string): Observable<any> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('role', role);
    return this.http.post(`${this.apiUrl}/start-interview`, formData);
  }

  submitAnswer(sessionId: string, question: string, answer: string): Observable<any> {
    return this.http.post(`${this.apiUrl}/submit-answer`, {
      session_id: sessionId,
      question: question,
      answer: answer
    });
  }

  getSummary(sessionId: string): Observable<any> {
    return this.http.get(`${this.apiUrl}/summary/${sessionId}`);
  }
}
