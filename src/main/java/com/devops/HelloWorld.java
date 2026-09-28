package com.devops;

public final class HelloWorld {
    private HelloWorld() {
    }

    public static String message() {
        return "Hello from Jenkins and Maven CI";
    }

    public static void main(String[] args) {
        System.out.println(message());
    }
}
