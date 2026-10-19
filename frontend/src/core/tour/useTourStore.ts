import { create } from 'zustand';

export interface TourState {
  isOpen: boolean;
  currentStepIndex: number;
  startTour: () => void;
  closeTour: () => void;
  nextStep: (totalSteps: number) => void;
  prevStep: () => void;
  goToStep: (index: number) => void;
}

export const useTourStore = create<TourState>((set, get) => ({
  isOpen: false,
  currentStepIndex: 0,

  startTour: () => {
    set({ isOpen: true, currentStepIndex: 0 });
  },

  closeTour: () => {
    set({ isOpen: false, currentStepIndex: 0 });
  },

  nextStep: (totalSteps: number) => {
    const { currentStepIndex } = get();
    if (currentStepIndex + 1 < totalSteps) {
      set({ currentStepIndex: currentStepIndex + 1 });
    } else {
      set({ isOpen: false, currentStepIndex: 0 });
    }
  },

  prevStep: () => {
    const { currentStepIndex } = get();
    if (currentStepIndex > 0) {
      set({ currentStepIndex: currentStepIndex - 1 });
    }
  },

  goToStep: (index: number) => {
    set({ currentStepIndex: Math.max(0, index) });
  },
}));

export default useTourStore;
