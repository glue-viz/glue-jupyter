<template>
    <v-btn-toggle v-model="active_tool_id" class="transparent">
        <v-tooltip v-for="[id, {tooltip, img}] of Object.entries(tools_data)" location="bottom">
            <template v-slot:activator="{ props }">
                <v-btn v-bind="props" icon :value="id">
                    <img :src="img" width="20"/>
                </v-btn>
            </template>
            <span>{{ tooltip }}</span>
        </v-tooltip>
    </v-btn-toggle>
</template>
