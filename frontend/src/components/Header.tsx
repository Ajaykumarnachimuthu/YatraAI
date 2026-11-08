import React from 'react';
import {
  Compass,
  Map as MapIcon,
  Bookmark,
  Sliders,
  LogIn,
  LogOut,
  User as UserIcon,
  Sparkles,
} from 'lucide-react';
import { HealthResponse, User } from '../types';

interface HeaderProps {
  activeView: 'planner' | 'trips' | 'explore' | 'profile';
  onNavigate: (view: 'planner' | 'trips' | 'explore' | 'profile') => void;
  health: HealthResponse | null;
  user: User | null;
  savedTripsCount: number;
  onOpenAuth: () => void;
  onLogout: () => void;
}

export const Header: React.FC<HeaderProps> = ({
  activeView,
  onNavigate,
  health,
  user,
  savedTripsCount,
  onOpenAuth,
  onLogout,
}) => {
  return (
    <header className="app-header">
      <div className="header-inner">
        {/* Brand Logo */}
        <div className="header-brand" onClick={() => onNavigate('planner')} style={{ cursor: 'pointer' }}>
          <div className="brand-logo-icon">
            <Compass size={22} />
          </div>
          <div>
            <div className="brand-name">
              YĀTRĀ <span className="brand-ai-badge">AI</span>
            </div>
            <div className="brand-tagline">
              Map-First Multimodal Travel Planner
            </div>
          </div>
        </div>

        {/* Center Main Navigation Bar */}
        <nav className="header-nav-menu">
          <button
            type="button"
            className={`nav-tab-btn ${activeView === 'planner' ? 'active' : ''}`}
            onClick={() => onNavigate('planner')}
          >
            <MapIcon size={16} />
            <span>Plan Journey</span>
          </button>

          <button
            type="button"
            className={`nav-tab-btn ${activeView === 'trips' ? 'active' : ''}`}
            onClick={() => onNavigate('trips')}
          >
            <Bookmark size={16} />
            <span>My Trips</span>
            {savedTripsCount > 0 && <span className="nav-count-badge">{savedTripsCount}</span>}
          </button>

          <button
            type="button"
            className={`nav-tab-btn ${activeView === 'explore' ? 'active' : ''}`}
            onClick={() => onNavigate('explore')}
          >
            <Compass size={16} />
            <span>Explore</span>
          </button>

          <button
            type="button"
            className={`nav-tab-btn ${activeView === 'profile' ? 'active' : ''}`}
            onClick={() => onNavigate('profile')}
          >
            <Sliders size={16} />
            <span>Travel Profile</span>
          </button>
        </nav>

        {/* Right Telemetry & User Controls */}
        <div className="header-right-controls">
          {/* ML Telemetry Pill */}
          <div className="telemetry-pill" title="HistGradientBoosting Decision Engine Status">
            <span className="pulse-dot-green" />
            <span className="telemetry-text">
              {health ? `ML Engine Active (τ=${health.decision_threshold})` : 'Connecting Engine...'}
            </span>
          </div>

          {/* User Sign In / Profile */}
          {user ? (
            <div className="user-profile-menu">
              <div className="user-avatar-tag">
                <UserIcon size={14} className="text-cyan" />
                <span className="user-email-text">{user.full_name || user.email.split('@')[0]}</span>
              </div>
              <button
                type="button"
                className="btn-icon-secondary"
                title="Sign Out"
                onClick={onLogout}
              >
                <LogOut size={15} />
              </button>
            </div>
          ) : (
            <button
              type="button"
              className="btn btn-secondary btn-sm"
              onClick={onOpenAuth}
            >
              <LogIn size={15} />
              <span>Sign In / Profile</span>
            </button>
          )}
        </div>
      </div>
    </header>
  );
};
