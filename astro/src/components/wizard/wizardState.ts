export interface SchedulePrefs {
  enabled: boolean;
  top_n: number;
}

export interface DailySchedulePrefs {
  time: string;
  utcOffsetMinutes: number;
  frequency: 'weekdays' | 'daily';
}

export interface WizardState {
  currentStep: number;
  briefing: {
    mode: 'academic' | 'personal';
    academicProfile: string;
  };
  selectedKeys: string[];
  config: Record<string, Record<string, unknown>>;
  llm: {
    provider: string;
    baseUrl: string;
    apiKeyEnv: string;
    scoringModel: string;
    summarizationModel: string;
  };
  arxiv: {
    presets: string[];
    customCategories: string[];
    customKeywords: string[];
    customBoosts: string[];
    threshold: number;
    maxPapers: number;
  };
  hacker_news: {
    min_score: number;
    max_items: number;
  };
  postdoc_jobs: {
    search_terms: string[];
    threshold: number;
  };
  supervisor_updates: {
    urls: string[];
  };
  schedule: {
    daily: DailySchedulePrefs;
    weekly: Record<string, SchedulePrefs>;
    monthly: Record<string, SchedulePrefs>;
  };
  global: {
    language: string;
  };
  sinks: {
    slack: {
      enabled: boolean;
      webhook: string;
      max_papers: number;
      max_hn: number;
      max_github: number;
    };
    serverchan: {
      enabled: boolean;
      sendkey: string;
      max_papers: number;
      max_hn: number;
      max_github: number;
      max_jobs: number;
    };
  };
  theme: {
    bgPreset: string;
    customBg: string;
    accentPreset: string;
    customAccent: string;
    customDark: boolean;
    darkBgPreset: string;
    customDarkBg: string;
    darkAccentPreset: string;
    customDarkAccent: string;
  };
}

export function createInitialState(): WizardState {
  return {
    currentStep: 1,
    briefing: {
      mode: 'academic',
      academicProfile: 'ai_ml',
    },
    selectedKeys: ['arxiv', 'hacker_news', 'github_trending'],
    config: {},
    llm: {
      provider: 'openrouter',
      baseUrl: 'https://openrouter.ai/api/v1',
      apiKeyEnv: 'OPENROUTER_API_KEY',
      scoringModel: 'google/gemini-2.5-flash-lite',
      summarizationModel: 'google/gemini-2.5-flash-lite',
    },
    arxiv: {
      presets: ['ai_ml'],
      customCategories: [],
      customKeywords: [],
      customBoosts: [],
      threshold: 7,
      maxPapers: 100,
    },
    hacker_news: { min_score: 100, max_items: 10 },
    postdoc_jobs: { search_terms: [], threshold: 6 },
    supervisor_updates: { urls: [] },
    schedule: {
      daily: { time: '09:30', utcOffsetMinutes: 0, frequency: 'weekdays' },
      weekly: {},
      monthly: {},
    },
    global: { language: 'en' },
    sinks: {
      slack: { enabled: false, webhook: '', max_papers: 5, max_hn: 3, max_github: 3 },
      serverchan: { enabled: false, sendkey: '', max_papers: 5, max_hn: 3, max_github: 3, max_jobs: 3 },
    },
    theme: {
      bgPreset: 'press',     customBg: '',
      accentPreset: 'robin', customAccent: '',
      customDark: true,
      darkBgPreset: 'ink',   customDarkBg: '',
      darkAccentPreset: 'robin', customDarkAccent: '',
    },
  };
}

export const DEFAULT_TOP_N: Record<string, number> = {
  weather: 1, arxiv: 7, github_trending: 5,
  hacker_news: 5, postdoc_jobs: 5, supervisor_updates: 5,
  quote_of_day: 1, hitokoto: 1, us_stocks: 6,
};
