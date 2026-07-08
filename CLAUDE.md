# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

An AI agent framework for the Disney Lorcana card game. The engine simulates full two-player games and exposes them to multiple agent types: rule-based heuristics, minimax with alpha-beta pruning, and MCTS via OpenSpiel.

## Dependencies

See `requirements.txt`. All dependencies install via pip: `pip install -r requirements.txt`. The `open_spiel` package provides both `pyspiel` and `open_spiel.python.algorithms`.

## Running the Game

```bash
# Interactive game (prompts for player names and controller types)
python play.py

# Run agent benchmarks (configure matchups and NUM_MATCHES in benchmark.py)
python benchmark.py
```

## Running Tests

Tests use Python's `unittest` framework and live in `test/`. Run from the project root:

```bash
# All tests
python -m pytest test/

# Single test file
python -m unittest test/test_challenging.py

# Single test case
python -m unittest test.test_challenging.TestChallenging.test_challenge_choices
```

Note: `test/test_support.py` contains shared fixtures (game setup helpers). It has a hardcoded `sys.path.insert` pointing to an old path — tests import from `test_support` directly (they insert the test dir into path themselves).

## Architecture

### Game Engine (no framework dependency)

- **`game.py` / `Game`** — Central state machine. Drives the full game loop via `get_actions()` → `process_action()`. Phases are defined in `game_enums.GamePhase`: `DIE_ROLL → DRAW_STARTING_HAND → MULLIGAN → MAIN` (with `CHALLENGING` and `CHOOSE_TARGET` sub-phases) → `GAME_OVER`.
- **`player.py` / `Player`** — Manages one player's hand, ink pool, in-play characters/items, and lore. All game actions (ink, play, quest, challenge) are methods here.
- **`action.py`** — Dataclasses for every action type (`InkAction`, `PlayCardAction`, `QuestAction`, `ChallengeAction`, `ChallengeTargetAction`, `TriggeredAbilityAction`, `AbilityTargetAction`, etc.).
- **`decklists.py`** — All card definitions (`CharacterCard`, `ActionCard`, `ItemCard`) and two pre-built decklists: `amber_amethyst` and `sapphire_steel`.
- **`ability.py`** — Ability class hierarchy. `TriggeredAbility` subclasses (`HealingTriggeredAbility`, `DamageTriggeredAbility`, etc.) implement `perform_ability()`. Passive/on-play abilities are checked inline.
- **`inplay_character.py`** — Wraps a `CharacterCard` in-play, tracking `ready`, `dry`, `damage`, `challenger_keyword`, `evasive`.
- **`exceptions.py`** — `TwentyLore` exception: raised by `player.perform_quest()` when lore ≥ 20; caught by `game.process_action()` to end the game.

### Controllers

Controllers implement `chooseAction(actions, game_state) -> action`. They are assigned to players and to the game as the `EnvironmentController` (handles die roll, draws, mulligans automatically).

- **`controller.py`** — Base `Controller`, `HumanController` (prompts stdin), `RandomController`, `EnvironmentController`.
- **`RuleBasedController.py`** — Runs all heuristics, picks highest-scoring action.

### Heuristics (`heuristic.py`)

Each heuristic has signature `(actions, gamestate) -> (index, score)` or `(None, 0.0)`. `combined_heuristic` runs `ALL_HEURISTICS` and returns the highest-scoring action index. `static_state_evaluation_heuristic` scores a board position numerically (used by minimax and MCTS evaluator).

### OpenSpiel Integration

- **`wrapper_state.py`** — `LorcanaState(pyspiel.State)` wraps `Game`. Actions are integer indices into `engine.get_actions()`. `LorcanaGame(pyspiel.Game)` produces initial states. Both classes are needed to use OpenSpiel algorithms.
- **`agents.py` / `make_agent()`** — Factory for `"mcts"`, `"minimax"`, or `"random"` agents. MCTS uses `HeuristicEvaluator` for value estimation and action priors.
- **`minimax_agent.py`** — Standalone alpha-beta minimax; works on `LorcanaState` via `clone()` / `apply_action()`.
- **`heuristic_eval.py` / `HeuristicEvaluator`** — OpenSpiel `Evaluator` adapter: `evaluate()` calls `static_state_evaluation_heuristic`, `prior()` calls `combined_heuristic` to generate action probabilities.

### Gym-Style Interface

- **`lorcana_env.py` / `LorcanaEnv`** — `reset()` / `step(action)` / `legal_actions()` interface for RL training.

### Supporting Modules

- **`game_state.py` / `state_extractor.py`** — Lightweight read-only snapshots of game state (used for logging/analysis, not for gameplay).
- **`contestant.py`** — Bundles a deck and a controller into a single object passed to `Game()`.
- **`visual_table.py`** — Board display utilities.
- **`benchmark.py`** — Agent head-to-head benchmarking harness.

## Key Patterns

**Action flow in `Game`**: `get_actions()` returns a list of action objects; the current controller's `chooseAction()` selects one; `process_action()` mutates state. OpenSpiel agents work with integer indices into this list.

**Ink system**: `ready_ink` is available ink. Playing a card subtracts from `ready_ink` and adds to `exerted_ink`. At draw phase, `ready_ink_cards()` moves `exerted_ink` back to `ready_ink`.

**Dry vs. Ready**: Characters enter play as `dry=False` (cannot quest/challenge on the turn they're played). `dry_characters()` is called at draw phase to make all characters dry. `ready` tracks whether a character is tapped.

**Two-interface duality**: The `RuleBasedController` can work with raw `Game` (old style, actions are objects) or via `LorcanaState` (OpenSpiel, actions are indices). It detects which mode via `hasattr(gamestate, "engine")`.
