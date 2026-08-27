import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { Topbar } from '../src/components/layout/topbar';

describe('Topbar', () => {
  it('renders search input', () => {
    render(<Topbar />);
    expect(screen.getByPlaceholderText('Search evaluations, traces...')).toBeInTheDocument();
  });

  it('renders avatar', () => {
    render(<Topbar />);
    expect(screen.getByText('SA')).toBeInTheDocument();
  });
});
