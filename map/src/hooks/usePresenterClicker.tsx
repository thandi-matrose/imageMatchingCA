import { useEffect } from "react";

type ClickerActions = {
  onNext: () => void;
  onPrev: () => void;
};

export const usePresenterClicker = ({ onNext, onPrev }: ClickerActions) => {
  useEffect(() => {
    // 1. Handle Keyboard (For actual presenter clickers)
    const handleKeyDown = (event: KeyboardEvent) => {
      switch (event.key) {
        case "PageDown":
        case "ArrowRight":
        case "ArrowDown":
        case "Enter":
        case " ":
          event.preventDefault();
          onNext();
          break;
        case "PageUp":
        case "ArrowLeft":
        case "ArrowUp":
        case "Backspace":
          event.preventDefault();
          onPrev();
          break;
        default:
          break;
      }
    };

    // 2. Handle Mouse Left Click (Next)
    const handleClick = (event: MouseEvent) => {
      const target = event.target as HTMLElement;

      // IMPORTANT: Ignore clicks on interactive elements
      // This prevents advancing the slide when you click a link, button, or the side menu
      if (
        target.closest("button") ||
        target.closest("a") ||
        target.closest(".side-menu") ||
        target.closest(".gif-container")
      ) {
        return;
      }

      onNext();
    };

    // 3. Handle Mouse Right Click (Previous)
    const handleContextMenu = (event: MouseEvent) => {
      const target = event.target as HTMLElement;

      // Ignore right clicks on interactive elements
      if (
        target.closest("button") ||
        target.closest("a") ||
        target.closest(".side-menu")
      ) {
        return;
      }

      event.preventDefault(); // Stop the browser's default right-click menu from appearing
      onPrev();
    };

    // Attach listeners
    window.addEventListener("keydown", handleKeyDown);
    window.addEventListener("click", handleClick);
    window.addEventListener("contextmenu", handleContextMenu);

    // Clean up on unmount
    return () => {
      window.removeEventListener("keydown", handleKeyDown);
      window.removeEventListener("click", handleClick);
      window.removeEventListener("contextmenu", handleContextMenu);
    };
  }, [onNext, onPrev]);
};
