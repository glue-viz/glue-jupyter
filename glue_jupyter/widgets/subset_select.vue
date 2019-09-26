<template>
    <v-menu>
        <template #activator="{ on }">
            <v-btn v-on="on" text v-if="selected.length > 0">
                <v-icon left :color="selected[0].color">signal_cellular_4_bar</v-icon>
                {{ selected[0].label }}
            </v-btn>
            <v-btn v-on="on" text v-else>{{ no_selection_text }}</v-btn>
        </template>
        <v-list>
            <v-list-item @click="selected = []">
                <v-list-item-title>
                    {{ no_selection_text }}
                </v-list-item-title>
            </v-list-item>
            <v-list-item v-for="item of available" @click="selected = [item]">
                <v-list-item-avatar>
                    <v-icon :color="item.color">signal_cellular_4_bar</v-icon>
                </v-list-item-avatar>
                <v-list-item-title>
                    {{ item.label }}
                </v-list-item-title>
            </v-list-item>
        </v-list>
    </v-menu>
</template>
