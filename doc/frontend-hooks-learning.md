# Frontend React Hooks: Concepts & Usage Guide

This document explains the core React Hooks implemented in the frontend application, what they do, and **why** they are essential for building a scalable and performant UI.

---

## 1. `useState`
**What it is:** A Hook that lets you add React state to function components.
**Why we use it:** To hold mutable data that changes over time (like user input, a toggled state, or a selected ID). When state updates, React knows it needs to re-render the component to reflect the new data in the UI.
*Example:* Managing the search input string or the currently selected post ID.

## 2. `useEffect`
**What it is:** A Hook that lets you perform side effects in function components. 
**Why we use it:** React components should primarily be pure functions. Whenever we need to step out of that boundary—for example, to fetch data from an external API, directly manipulate the DOM (like focusing an input), or set up a subscription—we use `useEffect`. It ensures these side effects happen safely *after* the render is committed to the screen.
*Example:* Triggering a data fetch when a component mounts, or automatically focusing the search input field.

## 3. `useRef`
**What it is:** A Hook that returns a mutable ref object whose `.current` property is initialized to the passed argument.
**Why we use it:** Unlike state, updating a `useRef` does **not** trigger a re-render. We use it for two main reasons:
1. **Accessing DOM Elements:** To directly interact with a DOM node (e.g., calling `.focus()` on an input field).
2. **Storing Mutable Values:** To keep track of values across renders without causing the UI to update when the value changes (e.g., keeping track of the previous state value).

## 4. `useMemo`
**What it is:** A Hook that memoizes (caches) the result of a calculation between renders.
**Why we use it:** For performance optimization. If you have an expensive calculation—like filtering a large list of posts based on a search query—you don't want to recalculate it every time the component re-renders for an unrelated reason. `useMemo` remembers the last result and only recalculates it if the dependencies (e.g., the raw list or the search query) change.

## 5. `useCallback`
**What it is:** A Hook that memoizes a function definition between renders.
**Why we use it:** In React, functions defined inside a component are recreated on every single render. If you pass these functions down as props to child components, it causes those child components to re-render unnecessarily because the function reference has changed. `useCallback` caches the function so its reference stays exactly the same, preventing useless re-renders in children.

## 6. `React.memo` (or `memo`)
**What it is:** A higher-order component that wraps a React component to memoize its rendered output.
**Why we use it:** By default, when a parent component re-renders, all of its children re-render too. Wrapping a child component in `memo` tells React: *"Only re-render this child if its props have actually changed."* When combined with `useCallback` (for function props) and primitive props, this provides massive performance gains for large lists (like mapping through `PostItem` components).

---

## Custom Hooks

Custom hooks allow us to extract component logic into reusable functions.

### `useFetch`
**Why we built it:** Fetching data involves repetitive boilerplate: handling loading states, catching errors, setting the data, and aborting stale requests. By extracting this into `useFetch`, any component can simply call `const { data, loading, error } = useFetch(url)` and immediately get safe, consistent API data without cluttering the component with complex `useEffect` logic.

### `usePrevious`
**Why we built it:** Sometimes the UI needs to compare the current state to what it *used* to be (for example, to show "Current Search" vs "Previous Search"). React doesn't store previous state natively. `usePrevious` uses `useRef` to store the previous value silently during a render cycle, giving us a clean, reusable way to access historical data.
