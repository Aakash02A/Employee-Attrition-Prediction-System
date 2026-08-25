package com.eaps.backend.model;

import jakarta.persistence.*;
import lombok.*;

/**
 * JPA entity for the {@code department} lookup table.
 * Values must match the categories the ML model was trained on:
 * "Human Resources", "Research &amp; Development", "Sales".
 */
@Entity
@Table(name = "department")
@Getter @Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class Department {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false, unique = true, length = 100)
    private String name;
}
