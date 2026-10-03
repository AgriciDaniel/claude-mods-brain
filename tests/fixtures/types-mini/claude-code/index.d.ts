// Written by Claude Code 9.9.1.
// Synthetic fixture for mods-brain adapter tests. Not a real capture.
declare module 'claude-code' {
  export type HookBudget = {
      /**
       * A hook's budget per dispatch: 10 seconds of its own time.
       */
      readonly ms: 10_000;
  };

  export type RenderComponent = 'AbovePrompt' | 'Pane';

  export interface CoreEngineInterface {
      /**
       * Display helpers.
       */
      ui: {
          /**
           * Shows a toast.
           */
          toast: (text: string) => void;
          resolve: (e: unknown) => unknown;
      };
      /**
       * The session.
       */
      session: {
          /**
           * Usage of the session. Free unless a breakdown is asked for.
           */
          usage: () => Promise<unknown>;
      };
  }

  export type Elements = {
      terminal: {
          Box: unknown;
          Text: unknown;
      };
      desktop: {
          Box: unknown;
          Svg: unknown;
      };
  };

  export type EngineEventOf = {
      /**
       * Fires when the engine is about to run a tool.
       */
      'tool.call': unknown;
      /**
       * Fires when a turn completes.
       */
      'turn.complete': unknown;
  };

  export type OpEventOf = {
      'ui.toast': unknown;
      'session.usage': unknown;
  };

  export type StopInput = {
      hook_event_name: 'Stop';
  };
}
