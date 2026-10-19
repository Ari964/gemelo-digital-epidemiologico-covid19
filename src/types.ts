export type PathogenType = 'covid19' | 'influenza_h5n1' | 'rsv';

export type UserRole = 'admin' | 'epidemiologist' | 'analyst' | 'policy_analyst' | 'viewer';

export type LanguageCode = 'es' | 'en' | 'sw';

export interface CountyData {
  id: string;
  name: string;
  code: number;
  population: number;
  areaKm2: number;
  density: number;
  latitude: number;
  longitude: number;
  urbanPercent: number;
  wealthQuintiles: {
    q1_poorest: number; // % in lowest quintile
    q2_second: number;
    q3_middle: number;
    q4_fourth: number;
    q5_wealthiest: number;
  };
  avgHouseholdSize: number;
  sharedWaterSanitationPercent: number; // DHS high risk factor
  icuBeds: number;
  icuBedsVerified?: number | null;
  icuSource?: string;
  populationSource?: string;
  isReferential?: boolean;
  generalBeds: number;
  mobilityConnectivityIndex?: number; // Gravitational mobility factor (Haversine & population)
  metaMobilityBaseline?: number; // Referential connectivity index (gravitational model)
}

export interface SimulationParams {
  id?: string;
  name: string;
  pathogen: PathogenType;
  durationDays: number;
  randomSeed: number;
  r0_baseline: number;
  latentPeriodDays: number; // 1 / sigma
  infectiousPeriodDays: number; // 1 / gamma
  hospitalizationRate: number;
  icuFractionOfHospitalized: number;
  icuStayDays: number;
  caseFatalityRatio: number;
  runMode?: 'EXPERIMENTAL' | 'OPERATIONAL';
  modelVersion?: string;
  
  // Interventions (NPIs & Pharmacological)
  interventions: {
    schoolClosure: {
      active: boolean;
      startDay: number;
      durationDays: number;
      complianceRate: number; // 0 - 1
      contactReductionSchool: number; // e.g. 0.75
    };
    vaccination: {
      active: boolean;
      startDay: number;
      dailyDosesPer10k: number;
      efficacyInfection: number; // e.g. 0.70
      efficacySevere: number; // e.g. 0.90
      strategy: 'age_prioritized' | 'occupation_prioritized' | 'random' | 'equity_targeted';
    };
    householdDistancing: {
      active: boolean;
      startDay: number;
      durationDays: number;
      complianceRate: number;
      adaptationForInformalSettlements: boolean; // community isolation centers rather than home lockdown
    };
    mobilityRestriction: {
      active: boolean;
      startDay: number;
      durationDays: number;
      interCountyReduction: number; // 0 - 1 (e.g. 0.60)
    };
    faceMasks: {
      active: boolean;
      startDay: number;
      coverage: number; // 0 - 1
      inwardEfficacy: number; // e.g. 0.40
      outwardEfficacy: number; // e.g. 0.60
    };
  };
}

export interface DailySimulationPoint {
  day: number;
  date: string;
  susceptible: number;
  exposed: number;
  infected: number;
  recovered: number;
  deceased: number;
  vaccinated: number;
  dailyNewCases: number;
  hospitalizedActive: number;
  icuActive: number;
  rt: number;
  mobilityIndex: number;
  // Disaggregated by wealth quintile
  q1Cases: number;
  q5Cases: number;
  q1Vaccinated: number;
  q5Vaccinated: number;
  hospitalSurgeExceeded: boolean;
}

export interface CountySimulationResult {
  countyId: string;
  countyName: string;
  totalCases: number;
  attackRate: number; // % infected
  totalHospitalizations: number;
  peakHospitalizations: number;
  peakIcuDemand: number;
  icuCapacity: number;
  icuExceededDays: number;
  totalDeaths: number;
  dalysLost: number;
  vaccinesAdministered: number;
  wealthQuintileBurden: {
    q1: number;
    q2: number;
    q3: number;
    q4: number;
    q5: number;
  };
  dailyTrajectory: {
    day: number;
    infected: number;
    dailyNewCases: number;
    hospitalized: number;
    icu: number;
    deaths: number;
  }[];
}

export interface SimulationResult {
  params: SimulationParams;
  executedAt: string;
  datasetHash: string;
  executionTimeMs: number;
  summary: {
    totalPopulation: number;
    totalInfections: number;
    attackRate: number;
    peakDay: number;
    peakInfected: number;
    totalHospitalizations: number;
    peakIcuBedDemand: number;
    totalIcuCapacity: number;
    daysIcuOverloaded: number;
    totalDeaths: number;
    mortalityPer100k: number;
    dalysAverted: number;
    demographicParityRatio: number; // Q1 vaccine access / Q5 vaccine access
    effectiveR0Mean: number;
  };
  nationalTrajectory: DailySimulationPoint[];
  countyResults: Record<string, CountySimulationResult>;
  isSynthetic?: boolean;
  isDemo?: boolean;
  runMode?: 'EXPERIMENTAL' | 'OPERATIONAL';
  isOperational?: boolean;
  model_version?: string;
  warning?: string | null;
  auditLogId?: string;
}

export interface AgentEntity {
  id: string;
  countyId: string;
  householdId: string;
  ageGroup: '0-17' | '18-49' | '50-64' | '65+';
  occupation: 'informal_worker' | 'essential_health' | 'market_vendor' | 'office' | 'student' | 'retired';
  wealthQuintile: 'q1' | 'q2' | 'q3' | 'q4' | 'q5';
  state: 'S' | 'E' | 'I' | 'R' | 'D';
  vaccinated: boolean;
  x: number;
  y: number;
  z: number;
  vx: number;
  vy: number;
  targetLocation: 'home' | 'school' | 'market' | 'clinic' | 'transit';
  householdDensityFactor: number;
  quarantined: boolean;
}

export interface SobolSensitivityResult {
  parameter: string;
  parameterName: string;
  firstOrderIndex: number; // S_i (main effect)
  totalOrderIndex: number; // S_Ti (total effect including interactions)
  confidenceInterval: [number, number];
  description: string;
}

export interface ValidationMetricSet {
  ksTest: {
    statistic: number;
    pValue: number;
    passed: boolean;
    description: string;
  };
  andersonDarling: {
    statistic: number;
    criticalValue5Percent: number;
    passed: boolean;
    description: string;
  };
  wilcoxonSignedRank: {
    wStatistic: number;
    pValue: number;
    digitalTwinMape: number;
    standardSeirMape: number;
    pImprovement: number;
  };
  forecastingHorizons: {
    oneWeek: { mape: number; rmse: number; r2: number };
    twoWeeks: { mape: number; rmse: number; r2: number };
    fourWeeks: { mape: number; rmse: number; r2: number };
  };
  aucRocHospitalOverflow: number;
  demographicParityRatio: {
    simulated: number;
    acceptableThresholdMin: number;
    acceptableThresholdMax: number;
  };
  sobolSensitivity: SobolSensitivityResult[];
}

export interface AuditLogEntry {
  id: string;
  timestamp: string;
  userRole?: UserRole | string;
  role?: string;
  userEmail?: string;
  user?: string;
  action: string;
  details?: string;
  parametersHash?: string;
  seed?: number;
  durationMs?: number;
  executionTimeMs?: number;
}

export interface UserAccount {
  id: string;
  name: string;
  email: string;
  role: 'admin' | 'epidemiologist' | 'analyst';
  status: 'active' | 'suspended';
  created_at?: string;
  createdAt?: string;
}

export interface AuditRecord {
  id: string;
  timestamp: string;
  userId: string;
  userEmail: string;
  userRole: string;
  action: string;
  parametersHash: string;
  seed: number;
  durationMs: number;
  details?: string;
}

export interface DatasetInfo {
  id: string;
  name: string;
  source: string;
  recordsCount: number;
  lastUpdated: string;
  status: 'loaded' | 'synthetic_fallback' | 'failed';
  coverage: string;
  coveragePct?: number;
  isSynthetic?: boolean;
  description: string;
}

export interface SyntheticMobilityMatrix {
  originCountyId: string;
  destinationCountyId: string;
  dailyCommuters: number;
  normalizedFlow: number;
}

export interface SyntheticDhsSurveyPoint {
  countyId: string;
  countyName: string;
  sampleSize: number;
  q1PovertyPercent: number;
  sharedSanitationPercent: number;
  underFiveMortalityPer1k: number;
  vaccineUptakeBaseline: number;
}


