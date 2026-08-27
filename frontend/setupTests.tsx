import '@testing-library/jest-dom'
import { vi } from 'vitest'

// Mock next/navigation
vi.mock('next/navigation', () => ({
  useRouter: () => ({
    push: vi.fn(),
    replace: vi.fn(),
    prefetch: vi.fn(),
    back: vi.fn(),
  }),
  usePathname: () => '/',
}))

// Mock lucide-react to avoid some SVG rendering issues
vi.mock('lucide-react', () => ({
  Shield: () => <div data-testid="lucide-shield" />,
  ArrowRight: () => <div data-testid="lucide-arrow-right" />,
  Eye: () => <div data-testid="lucide-eye" />,
  EyeOff: () => <div data-testid="lucide-eye-off" />,
  LayoutDashboard: () => <div data-testid="lucide-icon" />,
  FlaskConical: () => <div data-testid="lucide-icon" />,
  GitBranch: () => <div data-testid="lucide-icon" />,
  Bell: () => <div data-testid="lucide-icon" />,
  FileText: () => <div data-testid="lucide-icon" />,
  Settings: () => <div data-testid="lucide-icon" />,
  ChevronLeft: () => <div data-testid="lucide-icon" />,
  ChevronDown: () => <div data-testid="lucide-icon" />,
  Users: () => <div data-testid="lucide-icon" />,
  CreditCard: () => <div data-testid="lucide-icon" />,
}))
