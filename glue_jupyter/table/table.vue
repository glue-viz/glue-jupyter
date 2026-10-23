<template>
  <div class="glue-table-container">
    <!-- Cell display/edit bar (always visible) -->
    <div class="glue-edit-bar elevation-1">
      <div class="edit-bar-cell-ref">
        <v-icon size="small" class="mr-1">{{ selectedCell ? (selectedCell.editable ? 'mdi-table-edit' : 'mdi-table-eye') : 'mdi-table' }}</v-icon>
        <span class="edit-bar-label">{{ selectedCell ? selectedCell.column + ' [' + selectedCell.row + ']' : 'Click a cell to view' }}</span>
      </div>
      <div class="edit-bar-input-container">
        <v-text-field
          ref="editInput"
          v-model="editValue"
          class="edit-bar-input"
          density="compact"
          hide-details
          single-line
          variant="outlined"
          bg-color="white"
          :readonly="!selectedCell || !selectedCell.editable"
          :placeholder="selectedCell ? '' : 'Select a cell...'"
          @keyup.enter="onEnter"
          @keyup.escape="cancelEdit"
          @keydown.up.prevent="onArrow(-1)"
          @keydown.down.prevent="onArrow(1)"
        ></v-text-field>
      </div>
      <div class="edit-bar-actions" v-if="selectedCell && selectedCell.editable">
        <v-btn
          icon
          size="small"
          color="success"
          @click="commitEdit"
          title="Confirm and move to next row (Enter)"
        >
          <v-icon size="small">mdi-check</v-icon>
        </v-btn>
        <v-btn
          icon
          size="small"
          color="error"
          @click="cancelEdit"
          title="Cancel (Escape)"
        >
          <v-icon size="small">mdi-close</v-icon>
        </v-btn>
      </div>
    </div>

    <v-slide-x-transition appear>
      <v-data-table-server
        density="compact"
        :headers="[...headers]"
        :items="items"
        :items-per-page-options="[10, 20, 50, 100]"
        v-model:page="options.page"
        v-model:items-per-page="options.itemsPerPage"
        v-model:sort-by="tableSortBy"
        :items-length="total_length"
        :class="['elevation-1', 'glue-data-table', scrollable && 'glue-data-table--scrollable']"
        :style="scrollable && height != null && `height: ${height}`"
      >
      <template v-slot:headers="props">
          <tr>
            <th :style="'padding: 0 10px; width: '+Math.max(1, Math.ceil(Math.log10(total_length)))*20+'px'">#</th>
            <th style="padding: 0 1px; width: 30px" v-if="selection_enabled">
              <v-btn icon color="primary" variant="text" size="small" @click="toggle_select_all">
                <v-icon>{{ all_selected ? 'mdi-checkbox-marked' : (checked.length > 0 ? 'mdi-minus-box' : 'mdi-checkbox-blank-outline') }}</v-icon>
              </v-btn>
            </th>
            <th style="padding: 0 1px" v-for="(header, index) in headers_selections" :key="header.text">
              <v-icon style="padding: 0 1px" :key="index" :color="selection_colors[index]">mdi-circle</v-icon>
            </th>
            <th v-for="header in headers"
                :key="header.text"
                @click="onHeaderClick(header.value)"
                @mouseenter="hoverHeader = header.value"
                @mouseleave="hoverHeader = null"
                class="text-left text-no-wrap"
                style="cursor: pointer; user-select: none; padding: 0 8px; white-space: nowrap; position: relative;"
                :style="editingHeader === header.value ? {minWidth: '240px'} : {}"
            >
              {{ header.text }}
              <v-icon v-if="options.sortBy && options.sortBy[0] === header.value">
                {{ options.sortDesc && options.sortDesc[0] ? 'mdi-menu-down' : 'mdi-menu-up' }}
              </v-icon>
              <v-icon size="x-small" v-if="hoverHeader === header.value && editingHeader !== header.value && header.renameable" @click.stop="enterHeaderRename(header.value)" style="cursor:pointer;margin-left:2px" title="Rename column">mdi-pencil</v-icon>
              <v-icon size="x-small" v-if="hoverHeader === header.value && editingHeader !== header.value && header.removable" @click.stop="enterHeaderRemove(header.value)" style="cursor:pointer" title="Delete column">mdi-delete</v-icon>

              <!-- Rename mode: fills the th (min-width ensures it fits) -->
              <span v-if="editingHeader === header.value && headerMode === 'rename'" @click.stop style="position:absolute;top:0;left:0;right:0;bottom:0;display:inline-flex;align-items:center;gap:4px;background:white;padding:0 4px;z-index:1;"><input :data-header="header.value" v-model="headerEditValue" @keyup.enter.stop="acceptHeader(header.value)" @keyup.escape.stop="cancelHeader()" @click.stop class="glue-header-edit-input"/><v-icon size="x-small" @click.stop="cancelHeader()" style="cursor:pointer" title="Cancel (Esc)">mdi-close</v-icon><v-icon size="x-small" @click.stop="acceptHeader(header.value)" style="cursor:pointer" title="Accept (Enter)">mdi-check</v-icon></span>

              <!-- Delete confirmation: fills the th (min-width ensures it fits) -->
              <span v-if="editingHeader === header.value && headerMode === 'remove'" @click.stop style="position:absolute;top:0;left:0;right:0;bottom:0;display:inline-flex;align-items:center;gap:4px;background:#FFF3CD;border:1px solid #FFC107;padding:0 4px;z-index:1;font-size:11px;white-space:nowrap;"><v-icon size="x-small" style="color:#F57C00;">mdi-alert</v-icon><span>remove '{{ header.text }}'?</span><v-icon size="x-small" @click.stop="cancelHeader()" style="cursor:pointer" title="Cancel">mdi-close</v-icon><v-icon size="x-small" @click.stop="deleteHeader(header.value)" style="cursor:pointer" title="Confirm delete">mdi-delete</v-icon></span>
            </th>
          </tr>
      </template>
      <template v-slot:item="props">
        <tr @click="on_row_clicked(props.item.__row__)" :class="{'highlightedRow': props.item.__row__ === highlighted}">
          <td style="padding: 0 10px" class="text-left">
            <i>{{ props.item.__row__ }}</i>
          </td>
          <td style="padding: 0 1px; width: 30px" class="text-left" v-if="selection_enabled">
            <v-checkbox
              density="compact" hide-details style="margin-top: 0; padding-top: 0"
              :model-value="checked.indexOf(props.item.__row__) != -1"
              :key="props.item.__row__"
              @update:modelValue="(value) => select({checked: value, row: props.item.__row__})"
            />
          </td>
          <td style="padding: 0 1px" :key="header.text" v-for="(header, index) in headers_selections">
            <v-fade-transition leave-absolute>
              <v-icon
                v-if="props.item[header.value]"
                :color="selection_colors[index]"
              >mdi-circle</v-icon>
            </v-fade-transition>
          </td>
          <td v-for="header in headers"
              :key="header.text"
              class="text-left text-truncate text-no-wrap glue-selectable-cell"
              :class="{'glue-cell-selected': isSelected(props.item.__row__, header.value)}"
              :title="props.item[header.value]"
              @click.stop="selectCell(props.item.__row__, header.value, props.item[header.value], header.editable)"
          >{{ props.item[header.value] }}</td>
        </tr>
      </template>
      </v-data-table-server>
    </v-slide-x-transition>
  </div>
</template>

<script>
module.exports = {
  data: function() {
    return {
      selectedCell: null,   // { row: number, column: string, editable: boolean }
      editValue: '',
      hoverHeader: null,    // column value currently being hovered
      editingHeader: null,  // column value currently in rename/remove mode
      headerMode: null,     // 'rename' | 'remove' | null
      headerEditValue: ''   // live text in the rename input
    };
  },
  computed: {
    tableSortBy: {
      get() {
        const sortBy = Array.isArray(this.options.sortBy) ? this.options.sortBy : [];
        const sortDesc = Array.isArray(this.options.sortDesc) ? this.options.sortDesc : [];
        return sortBy.map((key, index) => ({
          key,
          order: sortDesc[index] ? 'desc' : 'asc'
        }));
      },
      set(sortByItems) {
        this.options = {
          ...this.options,
          sortBy: sortByItems.map(({key}) => key),
          sortDesc: sortByItems.map(({order}) => order === 'desc'),
          totalItems: this.total_length,
        };
      }
    }
  },
  watch: {
    items: function(newItems) {
      if (this.selectedCell === null) {
        return;
      }
      const item = newItems.find(item => item.__row__ === this.selectedCell.row);
      if (item === undefined || !(this.selectedCell.column in item)) {
        return;
      }
      const newValue = this.formatCellValue(item[this.selectedCell.column]);
      if (newValue === this.selectedCell.value) {
        return;
      }
      // Only refresh the input if the user has not started editing, so that
      // an unrelated data update does not discard an in-progress edit
      if (this.editValue === this.selectedCell.value) {
        this.editValue = newValue;
      }
      this.selectedCell.value = newValue;
    }
  },
  methods: {
    onOptionsUpdate(vuetifyOpts) {
      // Propagate page/itemsPerPage changes to Python; sort is handled by sort_column
      const newPage = vuetifyOpts.page;
      const newIpp = vuetifyOpts.itemsPerPage;
      if (newPage !== this.options.page || newIpp !== this.options.itemsPerPage) {
        this.options = { ...this.options, page: newPage, itemsPerPage: newIpp };
      }
    },
    // ---- header editing ----
    onHeaderClick(column) {
      if (this.editingHeader === null) { this.sort_column(column); }
    },
    enterHeaderRename(column) {
      // Use the bare column name rather than header.text, which includes any units
      this.headerEditValue = column;
      this.editingHeader = column;
      this.headerMode = 'rename';
      this.$nextTick(() => {
        const input = this.$el.querySelector(`input[data-header="${CSS.escape(column)}"]`);
        if (input) { input.focus(); input.select(); }
      });
    },
    enterHeaderRemove(column) {
      this.editingHeader = column;
      this.headerMode = 'remove';
    },
    acceptHeader(column) {
      const newName = this.headerEditValue.trim();
      this.editingHeader = null;
      this.headerMode = null;
      this.headerEditValue = '';
      if (newName && newName !== column) {
        this.rename_column({ column, newName });
      }
    },
    cancelHeader() {
      this.editingHeader = null;
      this.headerMode = null;
      this.headerEditValue = '';
    },
    deleteHeader(column) {
      this.editingHeader = null;
      this.headerMode = null;
      this.headerEditValue = '';
      this.remove_column({ column });
    },
    // ---- cell editing ----
    toggleSort(column) {
      this.sort_column(column);
    },
    formatCellValue(value) {
      return value !== null && value !== undefined ? String(value) : '';
    },
    selectCell(row, column, currentValue, editable) {
      const value = this.formatCellValue(currentValue);
      this.selectedCell = { row: row, column: column, editable: editable, value: value };
      this.editValue = value;
      // Focus the edit input after Vue updates the DOM so that keyboard
      // navigation works for both editable and read-only cells
      this.$nextTick(() => {
        if (this.$refs.editInput) {
          this.$refs.editInput.focus();
        }
      });
    },
    cancelEdit() {
      this.selectedCell = null;
      this.editValue = '';
    },
    commitEdit() {
      if (this.selectedCell && this.selectedCell.editable) {
        const currentColumn = this.selectedCell.column;
        const currentRow = this.selectedCell.row;
        // Commit the edit
        this.cell_edited({
          row: currentRow,
          column: currentColumn,
          value: this.editValue
        });
        this.advanceRow(1);
      }
    },
    onEnter() {
      if (this.selectedCell && this.selectedCell.editable) {
        this.commitEdit();
      } else {
        this.advanceRow(1);
      }
    },
    onArrow(step) {
      // Commit a pending edit before moving, as in a spreadsheet
      if (this.selectedCell && this.selectedCell.editable &&
          this.editValue !== this.selectedCell.value) {
        this.cell_edited({
          row: this.selectedCell.row,
          column: this.selectedCell.column,
          value: this.editValue
        });
      }
      this.advanceRow(step);
    },
    advanceRow(step) {
      // Move <step> rows in the same column, following the displayed order of
      // the rows (which may be sorted or filtered) rather than the row indices
      if (this.selectedCell) {
        const column = this.selectedCell.column;
        const index = this.items.findIndex(item => item.__row__ === this.selectedCell.row);
        const nextItem = index === -1 ? undefined : this.items[index + step];
        // At the first or last row of the current page, stay on the current cell
        if (nextItem) {
          this.selectCell(nextItem.__row__, column, nextItem[column], this.selectedCell.editable);
        }
      }
    },
    isSelected(row, column) {
      return this.selectedCell !== null &&
             this.selectedCell.row === row &&
             this.selectedCell.column === column;
    }
  }
}
</script>

<style id="glue_table">
/* Table container */
.glue-table-container {
  display: flex;
  flex-direction: column;
}

/* Edit bar (Excel-style formula bar) */
.glue-edit-bar {
  display: flex;
  align-items: center;
  padding: 4px 8px;
  background-color: #f5f5f5;
  border: 1px solid #e0e0e0;
  border-bottom: none;
  border-radius: 4px 4px 0 0;
  gap: 8px;
}

.edit-bar-cell-ref {
  display: flex;
  align-items: center;
  padding: 4px 8px;
  background-color: #fff;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  min-width: 120px;
  font-size: 12px;
  color: #666;
}

.edit-bar-label {
  font-family: monospace;
  font-weight: 500;
}

.edit-bar-input-container {
  flex: 1;
}

.edit-bar-input {
  margin: 0;
  padding: 0;
}

.edit-bar-input .v-field,
.edit-bar-input .v-field__input {
  min-height: 32px !important;
}

.edit-bar-actions {
  display: flex;
  gap: 4px;
}

.highlightedRow {
    background-color: #E3F2FD;
}

.glue-data-table {
  min-height: 250px;
}

.glue-data-table .v-table__wrapper {
  overflow-x: auto;
}

.glue-data-table table {
  table-layout: auto;
}

.glue-data-table th,
.glue-data-table td {
  white-space: nowrap;
  max-width: 300px;
  overflow: hidden;
  text-overflow: ellipsis;
  height: 28px !important;
}

.glue-data-table .v-selection-control {
  min-height: 28px;
}

.glue-data-table .v-selection-control__wrapper {
  height: 28px;
}

.glue-data-table--scrollable .v-table__wrapper {
  overflow-y: auto;
  height: calc(100% - 59px);
}

.glue-data-table--scrollable thead > tr {
  position: sticky;
  top: 0;
}

.glue-data-table--scrollable .v-table__wrapper,
.glue-data-table--scrollable .v-table__wrapper > table,
.glue-data-table--scrollable .v-table__wrapper > table thead,
.glue-data-table--scrollable .v-table__wrapper > table thead *
{
  background-color: inherit;
}

/* prevent checkboxes overlaying the table header */
.glue-data-table--scrollable .v-table__wrapper > table thead {
  position: relative;
  z-index: 1;
}

/* Selectable cell styles */
.glue-selectable-cell {
  cursor: pointer;
}

.glue-selectable-cell:hover {
  background-color: #f5f5f5;
}

/* Visual cue for selected cell */
.glue-cell-selected {
  background-color: #E3F2FD !important;
  box-shadow: inset 0 0 0 2px #1976D2;
}

/* ---- Column header rename / delete styles ---- */
.glue-header-edit-input {
  font-size: 12px;
  border: 1px solid #90CAF9;
  border-radius: 3px;
  padding: 1px 5px;
  width: 110px;
  outline: none;
  vertical-align: middle;
  background: #fff;
}

.glue-header-edit-input:focus {
  border-color: #1976D2;
  box-shadow: 0 0 0 2px rgba(25, 118, 210, 0.2);
}
</style>
