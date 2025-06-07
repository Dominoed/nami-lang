# Nami Programming Language

Nami is a modern, easy-to-learn language and compiler for building web apps, games, and desktop applications.  
**Author:** Brandon Postlethwait  
**License:** GPLv3

---

## Features

- Simple YAML-inspired indentation and custom block syntax
- Compile to HTML/CSS/JS (run in any browser)
- **Standalone desktop apps:** with Electron shell (Win/Linux)
- **Reactive variables:** `{score}` in UI auto-updates on change
- **Game/main loop:** for real-time logic
- **Advanced logic:**  
  - If/else (`<-if cond-> ... <-else-> ... </-if->`)
  - Loops (`<-for item in items-> ... </-for->`)
- All major layouts: `flex:`, `grid:`, `box:`, `row:`, `col:`, `spacer:`
- All major UI components: `text`, `button`, `input`, `textarea`, `checkbox`, `select/option`, `image`, `audio`, `video`
- **Multipage apps:** with auto-generated navigation
- Asset collection: images, audio, video copied to `build/assets/`

---

## Installation

**Windows:**
- Install [Python 3.10+](https://www.python.org/downloads/)
- Install [Node.js](https://nodejs.org/)
- (For Electron desktop: run `npm install` in `shells/electron`)

**Linux:**
```bash
sudo pacman -S python node
