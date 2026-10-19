import { describe, it, expect } from 'vitest';
import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { SimulationControls } from '../../src/components/SimulationControls';
import { getDefaultParams } from '../../src/utils/epidemicParams';
import { ToastProvider } from '../../src/components/ToastContainer';

describe('SimulationControls Component', () => {
  it('renders mobility controls and toggles synthetic warning banner', () => {
    const params = getDefaultParams('covid19');

    const { container } = render(
      <ToastProvider darkMode={true}>
        <SimulationControls
          currentParams={params}
          onRunSimulation={() => {}}
          isLoading={false}
          lang="es"
          darkMode={true}
        />
      </ToastProvider>
    );

    // Initial state: empirical (no banner)
    expect(container.querySelector('#banner_synthetic_data_warning')).toBeNull();

    // Click synthetic button
    const synBtn = container.querySelector('#btn_mobility_synthetic')!;
    fireEvent.click(synBtn);

    // Banner must appear
    const banner = container.querySelector('#banner_synthetic_data_warning');
    expect(banner).not.toBeNull();
    expect(screen.getByText(/DATOS SINTÉTICOS – NO VÁLIDOS PARA CONCLUSIONES CIENTÍFICAS/i)).toBeDefined();

    // Click empirical button
    const empBtn = container.querySelector('#btn_mobility_empirical')!;
    fireEvent.click(empBtn);

    // Banner must disappear
    expect(container.querySelector('#banner_synthetic_data_warning')).toBeNull();
  });
});
