<template>
    <v-menu :close-on-content-click="!multiple">

        <template #activator="{ on: menu }">
            <div v-on="menu" class="py-2 glue__subset-select">
                <v-chip v-if="selected.length === 0" style="cursor: pointer">
                    <v-icon left>add</v-icon>
                    {{ no_selection_text }}
                </v-chip>
                <v-tooltip v-else v-for="subset in toSubsets(selected)" :key=subset.label bottom>
                    <template #activator="{ on: tooltip }">
                        <v-chip v-on="(selected.length > nr_of_full_names) ? tooltip : {}" style="cursor: pointer">
                            <v-icon left :color="subset.color">
                                signal_cellular_4_bar
                            </v-icon>
                            {{ (selected.length <= nr_of_full_names) ? subset.label : '' }}
                        </v-chip>
                    </template>
                    {{ subset.label }}
                </v-tooltip>
            </div>
        </template>

        <v-list class="indigo--text">
            <v-list-item
                    @click="deselect"
                    :class="(selected.length === 0) ? 'v-list-item--active' : ''">
                <v-list-item-icon>
                    <v-icon>add</v-icon>
                </v-list-item-icon>
                <v-list-item-content>
                    <v-list-item-title>{{ no_selection_text }}</v-list-item-title>
                </v-list-item-content>
            </v-list-item>

            <v-list-item
                    v-for="(subset, index) in available"
                    :key="subset.label"
                    :class="(selected.includes(index)) ? 'v-list-item--active' : ''"
                    @click="toggleSubset(index)">
                <v-list-item-icon>
                    <v-icon :color="subset.color">signal_cellular_4_bar</v-icon>
                </v-list-item-icon>
                <v-list-item-content>
                    <v-list-item-title>
                        <span style="line-height: 2.2">{{ subset.label }}</span>
                        <v-btn icon @click.stop="remove_subset(index); toggleSubset(index)" class="float-right">
                            <v-icon>mdi-delete</v-icon>
                        </v-btn>
                    </v-list-item-title>
                </v-list-item-content>
            </v-list-item>

            <v-switch v-if="show_allow_multiple_subsets" v-model="multiple" label="Allow multiple subsets" @click="handleMultiple" class="px-4"></v-switch>
        </v-list>
    </v-menu>
</template>
