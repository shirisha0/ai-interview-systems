import { Component } from '@angular/core';
import { InterviewService } from './services/interview.service';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})
export class AppComponent {

  // Screens: 'upload' | 'interview' | 'summary'
  screen = 'upload';

  // Upload screen
  selectedFile: File | null = null;
  selectedRole = 'AI/ML Engineer';
  roles = ['AI/ML Engineer', 'Backend Engineer', 'Data Scientist', 'Full Stack Developer'];
  isLoading = false;
  errorMessage = '';

  // Interview screen
  sessionId = '';
  currentQuestion = '';
  questionNumber = 1;
  totalQuestions = 5;
  currentAnswer = '';

  // Summary screen
  summary: any = null;

  constructor(private interviewService: InterviewService) {}

  // ─────────────────────────────────────────────
  // Handle file selection
  // ─────────────────────────────────────────────
  onFileSelected(event: any) {
    this.selectedFile = event.target.files[0];
  }

  // ─────────────────────────────────────────────
  // Start interview
  // ─────────────────────────────────────────────
  startInterview() {
    if (!this.selectedFile) {
      this.errorMessage = 'Please upload your resume first.';
      return;
    }
    this.isLoading = true;
    this.errorMessage = '';

    this.interviewService.startInterview(this.selectedFile, this.selectedRole)
      .subscribe({
        next: (res) => {
          this.sessionId = res.session_id;
          this.currentQuestion = res.first_question;
          this.totalQuestions = res.total_questions;
          this.questionNumber = 1;
          this.screen = 'interview';
          this.isLoading = false;
        },
        error: (err) => {
          this.errorMessage = 'Something went wrong. Please try again.';
          this.isLoading = false;
        }
      });
  }

  // ─────────────────────────────────────────────
  // Submit answer
  // ─────────────────────────────────────────────
  submitAnswer() {
    if (!this.currentAnswer.trim()) {
      this.errorMessage = 'Please type your answer first.';
      return;
    }
    this.isLoading = true;
    this.errorMessage = '';

    this.interviewService.submitAnswer(
      this.sessionId,
      this.currentQuestion,
      this.currentAnswer
    ).subscribe({
      next: (res) => {
        this.currentAnswer = '';
        this.isLoading = false;

        if (res.status === 'completed') {
          this.loadSummary();
        } else {
          this.currentQuestion = res.next_question;
          this.questionNumber = res.question_number;
        }
      },
      error: (err) => {
        this.errorMessage = 'Something went wrong. Please try again.';
        this.isLoading = false;
      }
    });
  }

  // ─────────────────────────────────────────────
  // Load summary
  // ─────────────────────────────────────────────
  loadSummary() {
    this.interviewService.getSummary(this.sessionId)
      .subscribe({
        next: (res) => {
          this.summary = res;
          this.screen = 'summary';
        },
        error: (err) => {
          this.errorMessage = 'Could not load summary.';
        }
      });
  }

  // ─────────────────────────────────────────────
  // Restart interview
  // ─────────────────────────────────────────────
  restart() {
    this.screen = 'upload';
    this.selectedFile = null;
    this.currentAnswer = '';
    this.summary = null;
    this.errorMessage = '';
  }
}