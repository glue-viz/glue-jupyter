<template>
    <v-menu :close-on-content-click="!multiple">

        <template #activator="{ props: menu }">
            <div v-bind="menu" class="py-2 glue__subset-select">
                <v-chip v-if="selected.length === 0" style="cursor: pointer">
                    <v-icon start>add</v-icon>
                    {{ no_selection_text }}
                </v-chip>
                <v-tooltip v-else v-for="subset in toSubsets(selected)" :key=subset.label bottom>
                    <template #activator="{ props: tooltip }">
                        <v-chip v-bind="(selected.length > nr_of_full_names) ? tooltip : {}" style="cursor: pointer">
                            <v-icon start :color="subset.color">
                                signal_cellular_4_bar
                            </v-icon>
                            {{ (selected.length <= nr_of_full_names) ? subset.label : '' }}
                        </v-chip>
                    </template>
                    {{ subset.label }}
                </v-tooltip>
            </div>
        </template>

        <v-list class="text-indigo">
            <v-list-item
                    @click="deselect"
                    :class="(selected.length === 0) ? 'v-list-item--active' : ''">
                <template #prepend>
                    <v-icon>add</v-icon>
                </template>
                <v-list-item-title>{{ no_selection_text }}</v-list-item-title>
            </v-list-item>

            <v-list-item
                    v-for="(subset, index) in available"
                    :key="subset.label"
                    :class="(selected.includes(index)) ? 'v-list-item--active' : ''"
                    @click="toggleSubset(index)">
                <template #prepend>
                    <v-icon :color="subset.color">signal_cellular_4_bar</v-icon>
                </template>
                <v-list-item-title>
                    <span style="line-height: 2.2">{{ subset.label }}</span>
                </v-list-item-title>
                <template #append>
                    <v-btn icon @click.stop="remove_subset(index); toggleSubset(index)" class="float-right">
                        <v-icon>mdi-delete</v-icon>
                    </v-btn>
                </template>
            </v-list-item>

            <v-switch v-if="show_allow_multiple_subsets" v-model="multiple" label="Allow multiple subsets" @click="handleMultiple" class="px-4"></v-switch>
        </v-list>
    </v-menu>
</template>
