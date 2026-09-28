package com.devops;

import static org.junit.jupiter.api.Assertions.assertEquals;

import org.junit.jupiter.api.Test;

class HelloWorldTest {
    @Test
    void returnsTheExpectedCiMessage() {
        assertEquals("Hello from Jenkins and Maven CI", HelloWorld.message());
    }
}
