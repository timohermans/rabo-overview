import { render, screen } from '@testing-library/react';
import App from './App';

describe('App', () => {
  it('runs test suite', () => {
    render(<App />);

    expect(screen.getByText('Hello Vite + React!')).toBeInTheDocument();
  });
});
