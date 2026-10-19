import { SimulationParams, PathogenType } from '../types';

/**
 * Default parameter configurations per pathogen for UI controls
 */
export function getDefaultParams(pathogen: PathogenType = 'covid19'): SimulationParams {
  switch (pathogen) {
    case 'covid19':
      return {
        name: 'Baseline COVID-19 Wave',
        pathogen: 'covid19',
        durationDays: 120,
        randomSeed: 42,
        r0_baseline: 2.5,
        latentPeriodDays: 3.5,
        infectiousPeriodDays: 6.0,
        hospitalizationRate: 0.045,
        icuFractionOfHospitalized: 0.18,
        icuStayDays: 10,
        caseFatalityRatio: 0.014,
        interventions: {
          schoolClosure: {
            active: false,
            startDay: 15,
            durationDays: 45,
            complianceRate: 0.85,
            contactReductionSchool: 0.70,
          },
          vaccination: {
            active: true,
            startDay: 20,
            dailyDosesPer10k: 35,
            efficacyInfection: 0.72,
            efficacySevere: 0.91,
            strategy: 'age_prioritized',
          },
          householdDistancing: {
            active: false,
            startDay: 20,
            durationDays: 40,
            complianceRate: 0.60,
            adaptationForInformalSettlements: true,
          },
          mobilityRestriction: {
            active: false,
            startDay: 25,
            durationDays: 30,
            interCountyReduction: 0.50,
          },
          faceMasks: {
            active: true,
            startDay: 10,
            coverage: 0.65,
            inwardEfficacy: 0.40,
            outwardEfficacy: 0.60,
          },
        },
      };
    case 'influenza_h5n1':
      return {
        name: 'Pandemic Influenza Scenario',
        pathogen: 'influenza_h5n1',
        durationDays: 90,
        randomSeed: 101,
        r0_baseline: 1.85,
        latentPeriodDays: 2.0,
        infectiousPeriodDays: 4.5,
        hospitalizationRate: 0.065,
        icuFractionOfHospitalized: 0.22,
        icuStayDays: 7,
        caseFatalityRatio: 0.025,
        interventions: {
          schoolClosure: {
            active: true,
            startDay: 10,
            durationDays: 30,
            complianceRate: 0.90,
            contactReductionSchool: 0.80,
          },
          vaccination: {
            active: false,
            startDay: 30,
            dailyDosesPer10k: 20,
            efficacyInfection: 0.55,
            efficacySevere: 0.80,
            strategy: 'occupation_prioritized',
          },
          householdDistancing: {
            active: false,
            startDay: 15,
            durationDays: 25,
            complianceRate: 0.55,
            adaptationForInformalSettlements: true,
          },
          mobilityRestriction: {
            active: false,
            startDay: 20,
            durationDays: 20,
            interCountyReduction: 0.40,
          },
          faceMasks: {
            active: true,
            startDay: 5,
            coverage: 0.70,
            inwardEfficacy: 0.35,
            outwardEfficacy: 0.55,
          },
        },
      };
    case 'rsv':
    default:
      return {
        name: 'Seasonal RSV Surge (Pediatric High-Impact)',
        pathogen: 'rsv',
        durationDays: 100,
        randomSeed: 77,
        r0_baseline: 1.6,
        latentPeriodDays: 4.0,
        infectiousPeriodDays: 5.5,
        hospitalizationRate: 0.08,
        icuFractionOfHospitalized: 0.15,
        icuStayDays: 6,
        caseFatalityRatio: 0.008,
        interventions: {
          schoolClosure: {
            active: true,
            startDay: 12,
            durationDays: 28,
            complianceRate: 0.80,
            contactReductionSchool: 0.65,
          },
          vaccination: {
            active: true,
            startDay: 1,
            dailyDosesPer10k: 15,
            efficacyInfection: 0.60,
            efficacySevere: 0.88,
            strategy: 'equity_targeted',
          },
          householdDistancing: {
            active: false,
            startDay: 10,
            durationDays: 30,
            complianceRate: 0.50,
            adaptationForInformalSettlements: true,
          },
          mobilityRestriction: {
            active: false,
            startDay: 15,
            durationDays: 20,
            interCountyReduction: 0.30,
          },
          faceMasks: {
            active: false,
            startDay: 1,
            coverage: 0.40,
            inwardEfficacy: 0.30,
            outwardEfficacy: 0.50,
          },
        },
      };
  }
}
