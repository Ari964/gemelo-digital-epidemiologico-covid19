import { describe, it, expect } from 'vitest';
import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { FloatingChatbot } from '../../src/components/FloatingChatbot';

describe('FloatingChatbot Component', () => {
  it('renders permanently fixed trigger in bottom-right corner', () => {
    const { container } = render(<FloatingChatbot darkMode={true} />);
    
    const trigger = container.querySelector('#btn_floating_chatbot_trigger');
    expect(trigger).not.toBeNull();
    
    const root = container.querySelector('#floating_chatbot_root');
    expect(root?.className).toContain('fixed');
    expect(root?.className).toContain('bottom-6');
    expect(root?.className).toContain('right-6');
  });

  it('opens chat window when floating trigger is clicked', () => {
    const { container } = render(<FloatingChatbot darkMode={true} />);

    const trigger = container.querySelector('#btn_floating_chatbot_trigger')!;
    fireEvent.click(trigger);

    const chatWindow = container.querySelector('#floating_chat_window');
    expect(chatWindow).not.toBeNull();
    expect(screen.getByText(/AI Epidemiologist Copilot/i)).toBeDefined();
    expect(container.querySelector('#input_floating_chat_message')).not.toBeNull();
  });
});
