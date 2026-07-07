# Dance Scheduler 📅💃

A smart, interactive web application built with FastAPI and SQLite to help dance coordinators plan, optimize, and schedule practice sessions. It automatically detects scheduling conflicts based on dancer availability and allows organizers to easily reorder sessions via drag-and-drop.

---

## 🚀 Key Features

* **Smart Auto-Generation**: Generate a schedule draft automatically based on a custom time window (e.g., 18:00 to 02:00) and highlight priority routines.
* **Interactive Drag-and-Drop**: Reorder practice sessions on the fly. Clock times and conflicts are recalculated in real-time using [SortableJS](https://sortablejs.github.io/Sortable/).
* **Double-Layer Conflict Detection**:
  * **Roster Constraints**: Everyday recurring busy hours for dancers.
  * **Daily Constraints**: Date-specific, one-off time conflicts for individual dancers.
* **Dance Library**: Register dancers, define custom groups/routines, and manage dancer names and availability.
* **Print-Friendly View**: A custom print stylesheet formats the schedule as a clean, paper-ready itinerary (hides setup options and buttons).

---

## 🛠️ Setup & Installation

### 1. Prerequisites
Ensure you have **Python 3.8+** installed.

### 2. Clone and Setup Environment
Navigate to the project root directory and create a virtual environment:

```bash
# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies
Install all required Python packages:

```bash
pip install -r requirements.txt
```

---

## 🏃 Running the Application

Start the local Uvicorn development server:

```bash
uvicorn app.main:app --reload
```

Once started, open your browser and navigate to:
👉 **[http://127.0.0.1:8000](http://127.0.0.1:8000)**

---

## 📖 How to Use

### Step 1: Create an Event
On the home page, enter a name for your upcoming rehearsal event (e.g., "Spring Showcase Technicals") and click **Create**. Click on your event to open its workspace.

### Step 2: Set Up your Roster (Setup Roster Tab)
Switch to the **Setup Roster** tab:
1. **Register Dancers**: Add all participating dancers by name.
2. **Set Busy Times**: For any dancer with general constraints, click **Times** under *Roster Management* to specify when they are unavailable (e.g., `18:00-19:00`).
3. **Define Dance Groups**: Create dance routines/groups, give them a name, select the participating dancers, and click **Save Group**.

### Step 3: Schedule Rehearsals (Planner Tab)
Switch back to the **Planner** tab:
* **Manual Entry**: Select a dance group, set its duration (minutes), or set a fixed custom time range (e.g. `20:00-20:45`), then click **Schedule Now**.
* **Smart Auto-Generation**: Define the overall window of your rehearsals (Start and End times), check which dances are "today's priority", and click **Generate Optimized Plan**.
* **Daily Conflicts**: Add temporary, today-only constraints for dancers under **Today's Individual Constraints**.
* **Adjust & Reorder**: Drag any practice card up or down to change the order. The schedule's times and any resulting conflicts (marked in red) will update automatically.

### Step 4: Export
Click **Print / Save PDF** to print a hard copy of the schedule or save it as a PDF. The layout automatically cleans itself up for print media.

---

## 🧪 Running Tests

The scheduling engine and conflict resolution are covered by unit tests. To run them:

```bash
python test_scheduler.py
```
