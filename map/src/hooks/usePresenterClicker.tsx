import { useEffect } from "react";

type ClickerActions = {
  onNext: () => void;
  onPrev: () => void;
};

export const usePresenterClicker = ({ onNext, onPrev }: ClickerActions) => {
  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      switch (event.key) {
        case "PageDown":
        case "ArrowRight":
        case "ArrowDown":
        case " ":
          event.preventDefault();
          onNext();
          break;
        case "PageUp":
        case "ArrowLeft":
        case "ArrowUp":
          event.preventDefault();
          onPrev();
          break;
        default:
          break;
      }
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => {
      window.removeEventListener("keydown", handleKeyDown);
    };
  }, [onNext, onPrev]);
};
