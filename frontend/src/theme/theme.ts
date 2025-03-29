import { createTheme, ThemeOptions } from '@mui/material/styles';

// Custom color palette
const colors = {
  primary: {
    main: '#1976d2',
  },
  secondary: {
    main: '#dc004e',
  },
  background: {
    default: '#f5f5f5',
  },
};

// Custom typography
const typography = {
  fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
  h1: {
    fontSize: '2.5rem',
    fontWeight: 500,
    lineHeight: 1.2,
  },
  h2: {
    fontSize: '2rem',
    fontWeight: 500,
    lineHeight: 1.3,
  },
  h3: {
    fontSize: '1.75rem',
    fontWeight: 500,
    lineHeight: 1.4,
  },
  h4: {
    fontSize: '1.5rem',
    fontWeight: 500,
    lineHeight: 1.5,
  },
  h5: {
    fontSize: '1.25rem',
    fontWeight: 500,
    lineHeight: 1.6,
  },
  h6: {
    fontSize: '1rem',
    fontWeight: 500,
    lineHeight: 1.7,
  },
  button: {
    textTransform: 'none' as const,
    fontWeight: 500,
  },
};

// Custom component styles
const components = {
  MuiButton: {
    styleOverrides: {
      root: {
        borderRadius: 8,
        padding: '8px 16px',
        transition: 'all 0.2s ease-in-out',
        '&:hover': {
          transform: 'translateY(-1px)',
          boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
        },
      },
      contained: {
        boxShadow: '0 2px 4px rgba(0, 0, 0, 0.1)',
        '&:hover': {
          boxShadow: '0 4px 8px rgba(0, 0, 0, 0.2)',
        },
      },
    },
  },
  MuiPaper: {
    styleOverrides: {
      root: {
        backgroundImage: 'none',
      },
    },
  },
  MuiTab: {
    styleOverrides: {
      root: {
        textTransform: 'none' as const,
        fontWeight: 500,
        variants: [],
      },
    },
  },
};

const shadows: ["none", string, string, string, string, string, string, string, string, string, string, string, string, string, string, string, string, string, string, string, string, string, string, string, string] = [
  'none',
  '0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06)',
  '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
  '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
  '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)',
  '0 25px 50px -12px rgba(0, 0, 0, 0.25)',
  '0 30px 60px -12px rgba(0, 0, 0, 0.25)',
  '0 35px 70px -12px rgba(0, 0, 0, 0.25)',
  '0 40px 80px -12px rgba(0, 0, 0, 0.25)',
  '0 45px 90px -12px rgba(0, 0, 0, 0.25)',
  '0 50px 100px -12px rgba(0, 0, 0, 0.25)',
  '0 55px 110px -12px rgba(0, 0, 0, 0.25)',
  '0 60px 120px -12px rgba(0, 0, 0, 0.25)',
  '0 65px 130px -12px rgba(0, 0, 0, 0.25)',
  '0 70px 140px -12px rgba(0, 0, 0, 0.25)',
  '0 75px 150px -12px rgba(0, 0, 0, 0.25)',
  '0 80px 160px -12px rgba(0, 0, 0, 0.25)',
  '0 85px 170px -12px rgba(0, 0, 0, 0.25)',
  '0 90px 180px -12px rgba(0, 0, 0, 0.25)',
  '0 95px 190px -12px rgba(0, 0, 0, 0.25)',
  '0 100px 200px -12px rgba(0, 0, 0, 0.25)',
  '0 105px 210px -12px rgba(0, 0, 0, 0.25)',
  '0 110px 220px -12px rgba(0, 0, 0, 0.25)',
  '0 115px 230px -12px rgba(0, 0, 0, 0.25)',
  '0 120px 240px -12px rgba(0, 0, 0, 0.25)',
];

// Create theme
export const theme = createTheme({
  palette: colors,
  typography,
  components,
  shape: {
    borderRadius: 8,
  },
  shadows,
});
