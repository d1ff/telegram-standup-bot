<template>
    <b-container id="app">
    <b-row>
        <b-nav>
            <b-nav-item to="/">
                Home
            </b-nav-item>
            <b-nav-item to="/about">
                About
            </b-nav-item>
        </b-nav>
    </b-row>
    <router-view/>
    </b-container>
</template>

