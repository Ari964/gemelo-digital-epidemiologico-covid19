import { describe, it, expect } from 'vitest';
import React from 'react';
import { render, screen } from '@testing-library/react';
import { Sidebar } from '../../src/components/Sidebar';

describe('Sidebar Component', () => {
  it('renders all core CRISP-DM modules', () => {
    render(
      <Sidebar
        activeTab="scenario_deployment"
        onSelectTab={() => {}}
        isCollapsed={false}
        onToggleCollapse={() => {}}
        darkMode={true}
        onToggleTheme={() => {}}
        lang="es"
        role="admin"
      />
    );

    // Verify CRISP-DM and security modules
    expect(screen.getByText(/Seguridad & Usuarios/i)).toBeDefined();
    expect(screen.getByText(/Fase 1-3/i)).toBeDefined();
    expect(screen.getByText(/Fase 4: Gemelo Digital/i)).toBeDefined();
    expect(screen.getByText(/Fase 5: Validación/i)).toBeDefined();
    expect(screen.getByText(/Fase 6: Despliegue NPIs/i)).toBeDefined();
    expect(screen.getByText(/Informes/i)).toBeDefined();
  });

  it('verifies 3D view is labeled as Visualización Espacial 3D & GIS', () => {
    render(
      <Sidebar
        activeTab="3d_view"
        onSelectTab={() => {}}
        isCollapsed={false}
        onToggleCollapse={() => {}}
        darkMode={true}
        onToggleTheme={() => {}}
        lang="es"
        role="admin"
      />
    );

    expect(screen.getByText(/Visualización Espacial 3D & GIS/i)).toBeDefined();
  });

  it('ensures AI Copilot button is NOT present in the sidebar (only floating button allowed)', () => {
    const { container } = render(
      <Sidebar
        activeTab="scenario_deployment"
        onSelectTab={() => {}}
        isCollapsed={false}
        onToggleCollapse={() => {}}
        darkMode={true}
        onToggleTheme={() => {}}
        lang="es"
        role="admin"
      />
    );

    const copilotBtn = container.querySelector('#btn_sidebar_ai_copilot');
    expect(copilotBtn).toBeNull();
  });
});
