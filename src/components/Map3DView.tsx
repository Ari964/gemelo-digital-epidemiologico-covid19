import React, { useEffect, useRef, useState } from 'react';
import * as THREE from 'three';
import { KENYA_COUNTIES } from '../data/kenyaCounties';
import { SimulationResult, AgentEntity, LanguageCode } from '../types';
import { generatePopulationAgents } from '../utils/threeAgentGenerator';
import { translations } from '../i18n/translations';
import { Play, Pause, RotateCcw, ZoomIn, ZoomOut, Shield, Activity, Users, Home, School, Hospital, ShoppingBag } from 'lucide-react';

interface Map3DViewProps {
  simulationResult: SimulationResult | null;
  selectedCountyId: string;
  onSelectCounty: (countyId: string) => void;
  lang: LanguageCode;
  darkMode: boolean;
}

export const Map3DView: React.FC<Map3DViewProps> = ({
  simulationResult,
  selectedCountyId,
  onSelectCounty,
  lang,
  darkMode,
}) => {
  const t = translations[lang];
  const containerRef = useRef<HTMLDivElement>(null);
  const [isPlaying, setIsPlaying] = useState(true);
  const [currentSimDay, setCurrentSimDay] = useState(25);
  const [activePreset, setActivePreset] = useState<'national' | 'nairobi' | 'mombasa' | 'informal'>('national');
  const [selectedAgent, setSelectedAgent] = useState<AgentEntity | null>(null);
  const [viewMode, setViewMode] = useState<'3d_twin' | 'gis_choropleth'>('3d_twin');

  const randomSeed = simulationResult?.params?.randomSeed || 42;
  const agentsRef = useRef<AgentEntity[]>(generatePopulationAgents(220, randomSeed));
  const sceneRef = useRef<THREE.Scene | null>(null);
  const rendererRef = useRef<THREE.WebGLRenderer | null>(null);
  const cameraRef = useRef<THREE.PerspectiveCamera | null>(null);
  const agentMeshesRef = useRef<THREE.Mesh[]>([]);

  // Initialize Three.js scene
  useEffect(() => {
    if (!containerRef.current) return;
    const width = containerRef.current.clientWidth || 800;
    const height = containerRef.current.clientHeight || 550;

    // Scene
    const scene = new THREE.Scene();
    scene.background = new THREE.Color(darkMode ? 0x090d16 : 0xf8fafc);
    scene.fog = new THREE.FogExp2(darkMode ? 0x090d16 : 0xf8fafc, 0.015);
    sceneRef.current = scene;

    // Camera
    const camera = new THREE.PerspectiveCamera(45, width / height, 0.1, 1000);
    camera.position.set(0, 32, 42);
    camera.lookAt(0, 0, 0);
    cameraRef.current = camera;

    // Renderer
    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setSize(width, height);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    rendererRef.current = renderer;

    containerRef.current.replaceChildren(renderer.domElement);

    // Lights
    const ambientLight = new THREE.AmbientLight(darkMode ? 0xd0d8e8 : 0xffffff, darkMode ? 0.7 : 0.9);
    scene.add(ambientLight);

    const dirLight = new THREE.DirectionalLight(0xffffff, 1.2);
    dirLight.position.set(20, 40, 20);
    dirLight.castShadow = true;
    dirLight.shadow.mapSize.width = 1024;
    dirLight.shadow.mapSize.height = 1024;
    scene.add(dirLight);

    // Ground Grid & Terrain
    const gridHelper = new THREE.GridHelper(70, 35, darkMode ? 0x334155 : 0xcbd5e1, darkMode ? 0x1e293b : 0xe2e8f0);
    gridHelper.position.y = -0.01;
    scene.add(gridHelper);

    // County Ground Discs
    KENYA_COUNTIES.forEach((county) => {
      // Map latitude & longitude to local scene space
      const posX = (county.longitude - 36.8) * 12;
      const posZ = -(county.latitude + 1.2) * 12;
      
      const radius = Math.max(1.8, Math.sqrt(county.population) / 750);
      const discGeo = new THREE.CylinderGeometry(radius, radius, 0.3, 24);
      const isSelected = county.id === selectedCountyId;
      const discMat = new THREE.MeshStandardMaterial({
        color: isSelected ? 0x3b82f6 : (county.riskIndex > 80 ? 0xef4444 : (county.riskIndex > 70 ? 0xf59e0b : 0x10b981)),
        transparent: true,
        opacity: isSelected ? 0.85 : 0.35,
        roughness: 0.4,
      });
      const disc = new THREE.Mesh(discGeo, discMat);
      disc.position.set(posX, 0.1, posZ);
      disc.receiveShadow = true;
      scene.add(disc);

      // Node marker building
      const buildingGeo = new THREE.BoxGeometry(0.8, 1.4, 0.8);
      const buildingMat = new THREE.MeshStandardMaterial({
        color: darkMode ? 0x94a3b8 : 0x475569,
        metalness: 0.2,
      });
      const building = new THREE.Mesh(buildingGeo, buildingMat);
      building.position.set(posX, 0.8, posZ);
      building.castShadow = true;
      scene.add(building);
    });

    // Micro environment structures (Schools, Clinics, Markets)
    const facilities = [
      { type: 'clinic', x: -4, z: 2, color: 0xef4444, height: 2.2, label: 'Kenyatta National Hospital (ICU Hub)' },
      { type: 'clinic', x: 8, z: 12, color: 0xef4444, height: 1.8, label: 'Coast General Hospital Mombasa' },
      { type: 'school', x: -6, z: -4, color: 0x3b82f6, height: 1.5, label: 'Olympic Primary School (Kibera)' },
      { type: 'school', x: 4, z: -2, color: 0x3b82f6, height: 1.5, label: 'Alliance High School' },
      { type: 'market', x: 2, z: 5, color: 0xf59e0b, height: 1.2, label: 'Gikomba Market Hub' },
      { type: 'market', x: -8, z: 6, color: 0xf59e0b, height: 1.2, label: 'Kawangware Informal Market' },
    ];

    facilities.forEach(fac => {
      const geo = new THREE.BoxGeometry(1.4, fac.height, 1.4);
      const mat = new THREE.MeshStandardMaterial({
        color: fac.color,
        roughness: 0.3,
        emissive: fac.color,
        emissiveIntensity: 0.2,
      });
      const mesh = new THREE.Mesh(geo, mat);
      mesh.position.set(fac.x, fac.height / 2, fac.z);
      mesh.castShadow = true;
      scene.add(mesh);

      // Glow beacon ring
      const ringGeo = new THREE.RingGeometry(1.2, 1.5, 24);
      const ringMat = new THREE.MeshBasicMaterial({
        color: fac.color,
        side: THREE.DoubleSide,
        transparent: true,
        opacity: 0.6,
      });
      const ring = new THREE.Mesh(ringGeo, ringMat);
      ring.rotation.x = -Math.PI / 2;
      ring.position.set(fac.x, 0.05, fac.z);
      scene.add(ring);
    });

    // Agents Representation (Instanced / Mesh array)
    const agentMeshes: THREE.Mesh[] = [];
    const agentSphereGeo = new THREE.SphereGeometry(0.32, 16, 16);

    agentsRef.current.forEach((agent) => {
      let agentColor = 0x38bdf8; // Susceptible
      if (agent.state === 'E') agentColor = 0xfbbf24;
      else if (agent.state === 'I') agentColor = 0xf43f5e;
      else if (agent.state === 'R') agentColor = 0x10b981;
      else if (agent.state === 'D') agentColor = 0x64748b;
      if (agent.vaccinated) agentColor = 0x8b5cf6;

      const agentMat = new THREE.MeshStandardMaterial({
        color: agentColor,
        roughness: 0.2,
        emissive: agent.state === 'I' ? 0xf43f5e : 0x000000,
        emissiveIntensity: agent.state === 'I' ? 0.6 : 0.0,
      });
      const mesh = new THREE.Mesh(agentSphereGeo, agentMat);
      mesh.position.set(agent.x, agent.y, agent.z);
      mesh.castShadow = true;
      mesh.userData = { agent };
      scene.add(mesh);
      agentMeshes.push(mesh);
    });
    agentMeshesRef.current = agentMeshes;

    // Animation Loop
    let animationFrameId: number;
    let clock = new THREE.Clock();

    const animate = () => {
      animationFrameId = requestAnimationFrame(animate);
      const delta = clock.getDelta();
      const time = clock.getElapsedTime();

      // Agent wandering & infection pulse dynamics
      agentsRef.current.forEach((agent, idx) => {
        const mesh = agentMeshes[idx];
        if (!mesh) return;

        // Subtle Brownian motion around target hub
        agent.x += agent.vx * (isPlaying ? 1 : 0);
        agent.z += agent.vy * (isPlaying ? 1 : 0);

        // Boundary constraint
        if (Math.abs(agent.x) > 28) agent.vx *= -1;
        if (Math.abs(agent.z) > 28) agent.vy *= -1;

        mesh.position.x = agent.x;
        mesh.position.z = agent.z;
        mesh.position.y = 0.35 + Math.sin(time * 3 + idx) * 0.05;

        // Pulse scale for infected agents
        if (agent.state === 'I') {
          const scale = 1.0 + Math.sin(time * 6 + idx) * 0.25;
          mesh.scale.set(scale, scale, scale);
        } else {
          mesh.scale.set(1, 1, 1);
        }
      });

      renderer.render(scene, camera);
    };

    animate();

    const handleResize = () => {
      if (!containerRef.current || !renderer || !camera) return;
      const w = containerRef.current.clientWidth;
      const h = containerRef.current.clientHeight;
      camera.aspect = w / h;
      camera.updateProjectionMatrix();
      renderer.setSize(w, h);
    };

    window.addEventListener('resize', handleResize);

    return () => {
      window.removeEventListener('resize', handleResize);
      cancelAnimationFrame(animationFrameId);
      renderer.dispose();
    };
  }, [darkMode, selectedCountyId]);

  // Handle Camera Presets
  const setCameraPreset = (preset: 'national' | 'nairobi' | 'mombasa' | 'informal') => {
    setActivePreset(preset);
    if (!cameraRef.current) return;
    const camera = cameraRef.current;

    switch (preset) {
      case 'national':
        camera.position.set(0, 34, 44);
        camera.lookAt(0, 0, 0);
        break;
      case 'nairobi':
        camera.position.set(-2, 14, 18);
        camera.lookAt(-1, 0, 1);
        break;
      case 'mombasa':
        camera.position.set(10, 15, 20);
        camera.lookAt(8, 0, 12);
        break;
      case 'informal':
        camera.position.set(-6, 8, 10);
        camera.lookAt(-6, 0, 4);
        break;
    }
  };

  const selectedCounty = KENYA_COUNTIES.find(c => c.id === selectedCountyId) || KENYA_COUNTIES[0];
  const countySim = simulationResult.countyResults[selectedCountyId] || simulationResult.countyResults['nairobi'];

  return (
    <div id="map_3d_container" className="flex flex-col xl:flex-row gap-6 w-full">
      {/* 3D Scene Viewport */}
      <div className={`flex-1 relative rounded-2xl overflow-hidden border ${darkMode ? 'bg-slate-950 border-slate-800' : 'bg-slate-50 border-slate-200'} shadow-xl min-h-[520px] flex flex-col`}>
        {/* Floating Header Controls */}
        <div className="absolute top-4 left-4 right-4 z-10 flex flex-wrap items-center justify-between gap-3 pointer-events-none">
          <div className="flex items-center gap-2 pointer-events-auto bg-slate-900/80 backdrop-blur-md px-3.5 py-2 rounded-xl border border-slate-700/60 shadow-lg text-xs">
            <span className="inline-block w-2.5 h-2.5 rounded-full bg-emerald-400 animate-pulse"></span>
            <span className="font-semibold text-slate-200">{t.agentPopulation3D}</span>
            <span className="text-slate-400">| Day {currentSimDay} / {simulationResult.params.durationDays}</span>
          </div>

          <div className="flex items-center gap-2 pointer-events-auto">
            {/* View Mode Toggle */}
            <div className="flex bg-slate-900/80 backdrop-blur-md p-1 rounded-xl border border-slate-700/60 text-xs">
              <button
                id="btn_view_3d_twin"
                onClick={() => setViewMode('3d_twin')}
                className={`px-3 py-1.5 rounded-lg font-medium transition ${viewMode === '3d_twin' ? 'bg-blue-600 text-white shadow' : 'text-slate-400 hover:text-slate-200'}`}
              >
                3D Digital Twin
              </button>
              <button
                id="btn_view_gis"
                onClick={() => setViewMode('gis_choropleth')}
                className={`px-3 py-1.5 rounded-lg font-medium transition ${viewMode === 'gis_choropleth' ? 'bg-blue-600 text-white shadow' : 'text-slate-400 hover:text-slate-200'}`}
              >
                GIS Map Grid
              </button>
            </div>

            {/* Presets */}
            <div className="hidden sm:flex bg-slate-900/80 backdrop-blur-md p-1 rounded-xl border border-slate-700/60 text-xs gap-1">
              <button
                id="btn_preset_national"
                onClick={() => setCameraPreset('national')}
                className={`px-2.5 py-1.5 rounded-lg transition ${activePreset === 'national' ? 'bg-slate-700 text-white' : 'text-slate-400 hover:text-slate-200'}`}
              >
                Kenya
              </button>
              <button
                id="btn_preset_nairobi"
                onClick={() => setCameraPreset('nairobi')}
                className={`px-2.5 py-1.5 rounded-lg transition ${activePreset === 'nairobi' ? 'bg-slate-700 text-white' : 'text-slate-400 hover:text-slate-200'}`}
              >
                Nairobi
              </button>
              <button
                id="btn_preset_mombasa"
                onClick={() => setCameraPreset('mombasa')}
                className={`px-2.5 py-1.5 rounded-lg transition ${activePreset === 'mombasa' ? 'bg-slate-700 text-white' : 'text-slate-400 hover:text-slate-200'}`}
              >
                Mombasa
              </button>
              <button
                id="btn_preset_informal"
                onClick={() => setCameraPreset('informal')}
                className={`px-2.5 py-1.5 rounded-lg transition ${activePreset === 'informal' ? 'bg-slate-700 text-white' : 'text-slate-400 hover:text-slate-200'}`}
              >
                Kibera Twin
              </button>
            </div>
          </div>
        </div>

        {/* Canvas Render Root */}
        {viewMode === '3d_twin' ? (
          <div ref={containerRef} className="w-full h-full min-h-[480px] flex-1 cursor-grab active:cursor-grabbing" />
        ) : (
          /* GIS Interactive Subcounty Choropleth Map */
          <div className="p-6 grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-3 overflow-y-auto max-h-[500px] mt-14">
            {KENYA_COUNTIES.map((county) => {
              const res = simulationResult.countyResults[county.id];
              const isSelected = county.id === selectedCountyId;
              const isIcuOver = res && res.peakIcuDemand > county.icuBeds;

              return (
                <button
                  id={`county_card_${county.id}`}
                  key={county.id}
                  onClick={() => onSelectCounty(county.id)}
                  className={`text-left p-3.5 rounded-xl border transition-all ${
                    isSelected
                      ? 'bg-blue-600/20 border-blue-500 ring-2 ring-blue-400/30'
                      : darkMode ? 'bg-slate-900/60 border-slate-800 hover:border-slate-700' : 'bg-white border-slate-200 hover:border-slate-300'
                  }`}
                >
                  <div className="flex items-center justify-between mb-1">
                    <span className={`font-semibold text-xs truncate ${darkMode ? 'text-slate-200' : 'text-slate-800'}`}>{county.name}</span>
                    <span className={`text-[10px] px-1.5 py-0.5 rounded font-mono ${isIcuOver ? 'bg-red-900/60 text-red-300 border border-red-700' : darkMode ? 'bg-slate-800 text-slate-300' : 'bg-slate-100 text-slate-600'}`}>
                      {res ? `${res.attackRate}%` : '--'}
                    </span>
                  </div>
                  <div className={`text-[11px] flex items-center justify-between ${darkMode ? 'text-slate-400' : 'text-slate-500'}`}>
                    <span>Pop: {(county.population / 1e6).toFixed(2)}M</span>
                    <span className="text-blue-400 font-mono">ICU: {county.icuBeds}</span>
                  </div>
                  <div className={`mt-2 w-full h-1.5 rounded-full overflow-hidden ${darkMode ? 'bg-slate-800' : 'bg-slate-200'}`}>
                    <div
                      className={`h-full ${isIcuOver ? 'bg-red-500' : 'bg-emerald-500'}`}
                      style={{ width: `${Math.min(100, ((res?.peakIcuDemand || 0) / (county.icuBeds || 1)) * 100)}%` }}
                    />
                  </div>
                </button>
              );
            })}
          </div>
        )}

        {/* Bottom Legend & Status Bar */}
        <div className="p-3.5 bg-slate-900/90 backdrop-blur-md border-t border-slate-800 flex flex-wrap items-center justify-between gap-4 text-xs text-slate-300">
          <div className="flex flex-wrap items-center gap-3">
            <span className="flex items-center gap-1.5 font-medium">
              <span className="w-3 h-3 rounded-full bg-sky-400 inline-block shadow"></span>
              {t.susceptible}
            </span>
            <span className="flex items-center gap-1.5 font-medium">
              <span className="w-3 h-3 rounded-full bg-amber-400 inline-block shadow"></span>
              {t.exposed}
            </span>
            <span className="flex items-center gap-1.5 font-medium">
              <span className="w-3 h-3 rounded-full bg-rose-500 inline-block shadow animate-pulse"></span>
              {t.infected}
            </span>
            <span className="flex items-center gap-1.5 font-medium">
              <span className="w-3 h-3 rounded-full bg-emerald-400 inline-block shadow"></span>
              {t.recovered}
            </span>
            <span className="flex items-center gap-1.5 font-medium">
              <span className="w-3 h-3 rounded-full bg-violet-400 inline-block shadow"></span>
              {t.vaccinated}
            </span>
          </div>

          <div className="flex items-center gap-3">
            <div className="flex items-center gap-2">
              <span className="text-slate-400 font-mono text-[11px]">Timeline:</span>
              <input
                id="slider_sim_day"
                type="range"
                min="1"
                max={simulationResult.params.durationDays}
                value={currentSimDay}
                onChange={(e) => setCurrentSimDay(Number(e.target.value))}
                className="w-28 accent-blue-500 h-1.5 bg-slate-700 rounded-lg cursor-pointer"
              />
            </div>

            <button
              id="btn_play_pause_sim"
              onClick={() => setIsPlaying(!isPlaying)}
              className="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 transition"
              title={isPlaying ? 'Pause' : 'Play'}
            >
              {isPlaying ? <Pause size={14} /> : <Play size={14} />}
            </button>
          </div>
        </div>
      </div>

      {/* Selected County Digital Twin Detail Card */}
      <div className={`w-full xl:w-80 rounded-2xl p-5 border ${darkMode ? 'bg-slate-900/90 border-slate-800' : 'bg-white border-slate-200'} shadow-xl flex flex-col justify-between`}>
        <div>
          <div className="flex items-center justify-between mb-3">
            <div>
              <span className="text-[11px] font-mono uppercase tracking-wider text-blue-400 font-semibold">Subcounty Twin</span>
              <h3 className={`text-lg font-bold ${darkMode ? 'text-slate-100' : 'text-slate-900'}`}>{selectedCounty.name}</h3>
            </div>
            <div className="p-2 rounded-xl bg-blue-500/10 text-blue-400 border border-blue-500/20">
              <Activity size={20} />
            </div>
          </div>

          <p className={`text-xs mb-4 leading-relaxed ${darkMode ? 'text-slate-400' : 'text-slate-500'}`}>
            Population: <strong className={`${darkMode ? 'text-slate-200' : 'text-slate-800'}`}>{(selectedCounty.population).toLocaleString()}</strong> | Density: <strong className={`${darkMode ? 'text-slate-200' : 'text-slate-800'}`}>{selectedCounty.density} / km²</strong>
          </p>

          {/* Factores Demográficos y de Conectividad Espacial */}
          <div className="space-y-2.5 mb-4 text-xs">
            <div className={`p-2.5 rounded-xl flex items-center justify-between ${darkMode ? 'bg-slate-950/60 border border-slate-800' : 'bg-slate-50 border border-slate-200'}`}>
              <span className={`${darkMode ? 'text-slate-400' : 'text-slate-500'}`}>Pobreza Q1 (Estructural):</span>
              <span className="font-mono font-semibold text-amber-400">{(selectedCounty.wealthQuintiles.q1_poorest * 100).toFixed(0)}%</span>
            </div>
            <div className={`p-2.5 rounded-xl flex items-center justify-between ${darkMode ? 'bg-slate-950/60 border border-slate-800' : 'bg-slate-50 border border-slate-200'}`}>
              <span className={`${darkMode ? 'text-slate-400' : 'text-slate-500'}`}>Tamaño Promedio Hogar:</span>
              <span className={`font-mono font-semibold ${darkMode ? 'text-slate-200' : 'text-slate-800'}`}>{selectedCounty.avgHouseholdSize} personas</span>
            </div>
            <div className={`p-2.5 rounded-xl flex items-center justify-between ${darkMode ? 'bg-slate-950/60 border border-slate-800' : 'bg-slate-50 border border-slate-200'}`}>
              <span className={`${darkMode ? 'text-slate-400' : 'text-slate-500'}`}>Saneamiento Compartido:</span>
              <span className="font-mono font-semibold text-rose-400">{(selectedCounty.sharedWaterSanitationPercent * 100).toFixed(0)}%</span>
            </div>
            <div className={`p-2.5 rounded-xl flex items-center justify-between ${darkMode ? 'bg-slate-950/60 border border-slate-800' : 'bg-slate-50 border border-slate-200'}`}>
              <span className={`${darkMode ? 'text-slate-400' : 'text-slate-500'}`}>Conectividad Gravitacional:</span>
              <span className="font-mono font-semibold text-cyan-400">{selectedCounty.metaMobilityBaseline.toFixed(2)}x</span>
            </div>
          </div>

          {/* Simulated Twin Outcomes */}
          <div className={`border-t pt-3 ${darkMode ? 'border-slate-800' : 'border-slate-200'}`}>
            <span className={`text-[11px] font-semibold uppercase block mb-2 ${darkMode ? 'text-slate-400' : 'text-slate-500'}`}>Simulated Burden</span>
            <div className="grid grid-cols-2 gap-2 text-xs">
              <div className={`p-2 rounded-lg ${darkMode ? 'bg-slate-800/40' : 'bg-slate-100'}`}>
                <span className={`text-[10px] block ${darkMode ? 'text-slate-400' : 'text-slate-500'}`}>Total Cases</span>
                <span className={`text-sm font-bold font-mono ${darkMode ? 'text-slate-100' : 'text-slate-900'}`}>{countySim?.totalCases.toLocaleString() || '--'}</span>
              </div>
              <div className={`p-2 rounded-lg ${darkMode ? 'bg-slate-800/40' : 'bg-slate-100'}`}>
                <span className={`text-[10px] block ${darkMode ? 'text-slate-400' : 'text-slate-500'}`}>Attack Rate</span>
                <span className="text-sm font-bold text-emerald-400 font-mono">{countySim?.attackRate || '--'}%</span>
              </div>
              <div className={`p-2 rounded-lg ${darkMode ? 'bg-slate-800/40' : 'bg-slate-100'}`}>
                <span className={`text-[10px] block ${darkMode ? 'text-slate-400' : 'text-slate-500'}`}>Peak ICU Need</span>
                <span className={`text-sm font-bold font-mono ${(countySim?.peakIcuDemand || 0) > selectedCounty.icuBeds ? 'text-rose-400' : darkMode ? 'text-slate-100' : 'text-slate-900'}`}>
                  {countySim?.peakIcuDemand || '--'} / {selectedCounty.icuBeds}
                </span>
              </div>
              <div className={`p-2 rounded-lg ${darkMode ? 'bg-slate-800/40' : 'bg-slate-100'}`}>
                <span className={`text-[10px] block ${darkMode ? 'text-slate-400' : 'text-slate-500'}`}>DALYs Lost</span>
                <span className="text-sm font-bold text-amber-400 font-mono">{countySim?.dalysLost.toLocaleString() || '--'}</span>
              </div>
            </div>
          </div>
        </div>

        {/* Quick Micro-Node Selector */}
        <div className={`mt-4 pt-3 border-t ${darkMode ? 'border-slate-800' : 'border-slate-200'}`}>
          <label className={`text-[11px] mb-1 block font-medium ${darkMode ? 'text-slate-400' : 'text-slate-500'}`}>Select Subcounty Focus:</label>
          <select
            id="select_county_focus"
            value={selectedCountyId}
            onChange={(e) => onSelectCounty(e.target.value)}
            className={`w-full rounded-xl px-3 py-2 text-xs font-medium focus:ring-2 focus:ring-blue-500 outline-none ${darkMode ? 'bg-slate-950 border border-slate-700 text-slate-200' : 'bg-white border border-slate-300 text-slate-800 hover:border-slate-400'}`}
          >
            {KENYA_COUNTIES.map(c => (
              <option key={c.id} value={c.id}>{c.name} (Pop: {(c.population / 1e6).toFixed(1)}M)</option>
            ))}
          </select>
        </div>
      </div>
    </div>
  );
};
