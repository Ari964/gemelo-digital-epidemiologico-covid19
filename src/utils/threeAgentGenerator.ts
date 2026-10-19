import { AgentEntity } from '../types';

/**
 * Generate 3D Population Micro-Agents for Three.js Visualization
 */
export function generatePopulationAgents(count = 200, seed = 42): AgentEntity[] {
  const agents: AgentEntity[] = [];
  const ageGroups: ('0-17' | '18-49' | '50-64' | '65+')[] = ['0-17', '18-49', '50-64', '65+'];
  const ageWeights = [0.42, 0.40, 0.12, 0.06];
  const occupations: ('informal_worker' | 'essential_health' | 'market_vendor' | 'office' | 'student' | 'retired')[] = [
    'informal_worker', 'essential_health', 'market_vendor', 'office', 'student', 'retired'
  ];
  const wealths: ('q1' | 'q2' | 'q3' | 'q4' | 'q5')[] = ['q1', 'q2', 'q3', 'q4', 'q5'];

  for (let i = 0; i < count; i++) {
    const pseudoRand = (offset: number) => {
      const x = Math.sin(seed + i * 13.37 + offset) * 10000;
      return x - Math.floor(x);
    };

    const rAge = pseudoRand(1);
    let cumulative = 0;
    let age: '0-17' | '18-49' | '50-64' | '65+' = '18-49';
    for (let k = 0; k < ageGroups.length; k++) {
      cumulative += ageWeights[k];
      if (rAge <= cumulative) {
        age = ageGroups[k];
        break;
      }
    }

    const occupation = age === '0-17' ? 'student' : (age === '65+' ? 'retired' : occupations[Math.floor(pseudoRand(2) * 4)]);
    const wealth = wealths[Math.floor(pseudoRand(3) * 5)];
    
    let state: 'S' | 'E' | 'I' | 'R' | 'D' = 'S';
    const rState = pseudoRand(4);
    if (rState < 0.05) state = 'I';
    else if (rState < 0.12) state = 'E';
    else if (rState < 0.35) state = 'R';

    const householdIdx = Math.floor(i / 6);
    const hhAngle = (householdIdx * 0.45) % (Math.PI * 2);
    const hhRadius = 6 + (householdIdx % 4) * 5;
    const hhCenterX = Math.cos(hhAngle) * hhRadius;
    const hhCenterZ = Math.sin(hhAngle) * hhRadius;

    const localSpread = 1.8;
    const posX = hhCenterX + (pseudoRand(5) - 0.5) * localSpread;
    const posZ = hhCenterZ + (pseudoRand(6) - 0.5) * localSpread;
    const posY = 0.35;

    agents.push({
      id: `agent_${i}`,
      countyId: i < count / 2 ? 'nairobi' : 'mombasa',
      householdId: `hh_${householdIdx}`,
      ageGroup: age,
      occupation,
      wealthQuintile: wealth,
      state,
      vaccinated: pseudoRand(7) < 0.45,
      x: posX,
      y: posY,
      z: posZ,
      vx: (pseudoRand(8) - 0.5) * 0.04,
      vy: (pseudoRand(9) - 0.5) * 0.04,
      targetLocation: pseudoRand(10) > 0.6 ? 'market' : (pseudoRand(10) > 0.3 ? 'home' : 'transit'),
      householdDensityFactor: wealth === 'q1' ? 1.8 : 1.0,
      quarantined: false,
    });
  }

  return agents;
}
