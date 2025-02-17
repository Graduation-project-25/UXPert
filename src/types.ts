// src/types.ts
export interface ConsistencyResult {
    status: number;
    consistency_results: {
      Feedback: Record<string, string>;
    };
    error_prevention_results: {
      Feedback: Record<string, string>;
    };
    error_handling_results: {
      Feedback: Record<string, string>;
    };    
    minimalist_results: {
      Feedback: Record<string, string>;
    };
  }
  