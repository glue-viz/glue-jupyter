<template>
    <div class="glue-table-viewer-state">
        <v-select
            label="Visible columns"
            :items="column_items"
            v-model="visible_columns"
            multiple
            hide-details
        >
            <template v-slot:selection="{ index }">
                <span v-if="index === 0">
                    {{ visible_columns.length === column_items.length ? 'All columns' : `${visible_columns.length} of ${column_items.length} columns` }}
                </span>
            </template>
        </v-select>
    </div>
</template>
