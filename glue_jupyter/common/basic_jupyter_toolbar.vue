<template>
    <v-btn-toggle v-model="active_tool_id" class="transparent">
        <v-tooltip v-for="[id, {tooltip, img}] of Object.entries(tools_data)" bottom>
            <template v-slot:activator="{ on }">
                <v-btn v-on="on" icon :value="id">
                    <img :src="img" width="20"/>
                </v-btn>
            </template>
            <span>{{ tooltip }}</span>
        </v-tooltip>
    </v-btn-toggle>
</template>
