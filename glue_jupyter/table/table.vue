<template>
  <div class="glue-table-container">
    <!-- Edit bar (Excel-style formula bar) -->
    <v-slide-y-transition>
      <div v-if="editingCell" class="glue-edit-bar elevation-1">
        <div class="edit-bar-cell-ref">
          <v-icon small class="mr-1">mdi-table-edit</v-icon>
          <span class="edit-bar-label">{{ editingCell.column }} [{{ editingCell.row }}]</span>
        </div>
        <div class="edit-bar-input-container">
          <v-text-field
            ref="editInput"
            v-model="editValue"
            class="edit-bar-input"
            dense
            hide-details
            single-line
            outlined
            @keyup.enter="commitEdit"
            @keyup.escape="cancelEdit"
          ></v-text-field>
        </div>
        <div class="edit-bar-actions">
          <v-btn
            icon
            small
            color="success"
            @click="commitEdit"
            title="Confirm and move to next row (Enter)"
          >
            <v-icon small>mdi-check</v-icon>
          </v-btn>
          <v-btn
            icon
            small
            color="error"
            @click="cancelEdit"
            title="Cancel (Escape)"
          >
            <v-icon small>mdi-close</v-icon>
          </v-btn>
        </div>
      </div>
    </v-slide-y-transition>

    <v-slide-x-transition appear>
      <v-data-table
        dense
        hide-default-header
        :headers="[...headers]"
        :items="items"
        :footer-props="{'items-per-page-options': [10,20,50,100]}"
        :options.sync="options"
        :items_per_page.sync="items_per_page"
        :server-items-length="total_length"
        :class="['elevation-1', 'glue-data-table', scrollable && 'glue-data-table--scrollable']"
        :style="scrollable && height != null && `height: ${height}`"
      >
      <template v-slot:header="props">
        <thead>
          <tr>
            <th :style="'padding: 0 10px; width: '+Math.max(1, Math.ceil(Math.log10(total_length)))*20+'px'">#</th>
            <th style="padding: 0 1px; width: 30px" v-if="selection_enabled">
              <v-btn icon color="primary" text small @click="toggle_select_all">
                <v-icon>{{ all_selected ? 'check_box' : (checked.length > 0 ? 'indeterminate_check_box' : 'check_box_outline_blank') }}</v-icon>
              </v-btn>
            </th>
            <th style="padding: 0 1px" v-for="(header, index) in headers_selections" :key="header.text">
              <v-icon style="padding: 0 1px" :key="index" :color="selection_colors[index]">brightness_1</v-icon>
            </th>
            <th v-for="header in headers"
                :key="header.text"
                @click="toggleSort(header.value)"
                style="cursor: pointer; user-select: none;"
            >
              {{ header.text }}
              <v-icon v-if="options.sortBy && options.sortBy[0] === header.value">
                {{ options.sortDesc && options.sortDesc[0] ? 'arrow_drop_down' : 'arrow_drop_up' }}
              </v-icon>
            </th>
          </tr>
        </thead>
      </template>
      <template v-slot:item="props">
        <tr @click="on_row_clicked(props.item.__row__)" :class="{'highlightedRow': props.item.__row__ === highlighted}">
          <td style="padding: 0 10px" class="text-xs-left">
            <i>{{ props.item.__row__ }}</i>
          </td>
          <td style="padding: 0 1px" class="text-xs-left" v-if="selection_enabled">
            <v-checkbox
              hide-details style="margin-top: 0; padding-top: 0"
              :input-value="checked.indexOf(props.item.__row__) != -1"
              :key="props.item.__row__"
              @change="(value) => select({checked: value, row: props.item.__row__})"
            />
          </td>
          <td style="padding: 0 1px" :key="header.text" v-for="(header, index) in headers_selections">
            <v-fade-transition leave-absolute>
              <v-icon
                v-if="props.item[header.value]"
                v-model="props.item[header.value]"
                :color="selection_colors[index]"
              >brightness_1</v-icon>
            </v-fade-transition>
          </td>
          <td v-for="header in headers"
              :key="header.text"
              class="text-truncate text-no-wrap glue-editable-cell"
              :class="{'glue-cell-editing': isEditing(props.item.__row__, header.value)}"
              :title="props.item[header.value]"
          >
              <span class="cell-content">
                {{ props.item[header.value] }}
                <v-icon
                  v-if="header.editable"
                  x-small
                  class="edit-icon"
                  @click.stop="startEdit(props.item.__row__, header.value, props.item[header.value])"
                >mdi-pencil</v-icon>
              </span>
          </td>
        </tr>
      </template>
      </v-data-table>
    </v-slide-x-transition>
  </div>
</template>

<script>
module.exports = {
  data: function() {
    return {
      editingCell: null,  // { row: number, column: string }
      editValue: ''
    };
  },
  methods: {
    toggleSort(column) {
      this.sort_column(column);
    },
    startEdit(row, column, currentValue) {
      this.editingCell = { row: row, column: column };
      this.editValue = currentValue !== null && currentValue !== undefined ? String(currentValue) : '';
      // Focus the edit input after Vue updates the DOM
      this.$nextTick(() => {
        if (this.$refs.editInput) {
          this.$refs.editInput.focus();
        }
      });
    },
    cancelEdit() {
      this.editingCell = null;
      this.editValue = '';
    },
    commitEdit() {
      if (this.editingCell) {
        const currentColumn = this.editingCell.column;
        const currentRow = this.editingCell.row;
        // Commit the edit
        this.cell_edited({
          row: currentRow,
          column: currentColumn,
          value: this.editValue
        });
        // Move to the next row in the same column
        const nextRow = currentRow + 1;
        if (nextRow < this.total_length) {
          // Find the current value for the next cell
          const nextItem = this.items.find(item => item.__row__ === nextRow);
          if (nextItem) {
            this.startEdit(nextRow, currentColumn, nextItem[currentColumn]);
          } else {
            // Next row might not be in current page, just close editing
            this.editingCell = null;
            this.editValue = '';
          }
        } else {
          // No more rows, close editing
          this.editingCell = null;
          this.editValue = '';
        }
      }
    },
    isEditing(row, column) {
      return this.editingCell !== null &&
             this.editingCell.row === row &&
             this.editingCell.column === column;
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

.edit-bar-input .v-input__slot {
  min-height: 32px !important;
  background-color: #fff !important;
}

.edit-bar-actions {
  display: flex;
  gap: 4px;
}

.highlightedRow {
    background-color: #E3F2FD;
}

.glue-data-table .v-data-table__wrapper {
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
}

.glue-data-table--scrollable .v-data-table__wrapper {
  overflow-y: auto;
  height: calc(100% - 59px);
}

.glue-data-table--scrollable thead > tr {
  position: sticky;
  top: 0;
}

.glue-data-table--scrollable .v-data-table__wrapper,
.glue-data-table--scrollable .v-data-table__wrapper > table,
.glue-data-table--scrollable .v-data-table__wrapper > table thead,
.glue-data-table--scrollable .v-data-table__wrapper > table thead *
{
  background-color: inherit;
}

/* prevent checkboxes overlaying the table header */
.glue-data-table--scrollable .v-data-table__wrapper > table thead {
  position: relative;
  z-index: 1;
}

/* Editable cell styles */
.glue-editable-cell .cell-content {
  display: inline-flex;
  align-items: center;
}

.glue-editable-cell .edit-icon {
  opacity: 0;
  transition: opacity 0.2s;
  margin-left: 4px;
  cursor: pointer;
}

.glue-editable-cell:hover .edit-icon {
  opacity: 0.5;
}

.glue-editable-cell .edit-icon:hover {
  opacity: 1;
}

/* Visual cue for cell being edited */
.glue-cell-editing {
  background-color: #E3F2FD !important;
  box-shadow: inset 0 0 0 2px #1976D2;
}
</style>
