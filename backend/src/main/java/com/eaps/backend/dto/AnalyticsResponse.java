package com.eaps.backend.dto;

import lombok.*;

import java.util.List;
import java.util.Map;

/**
 * Generic chart data response used by the analytics page.
 * Frontend uses {@code labels} for axis/legend and {@code data} for values.
 */
@Getter @Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class AnalyticsResponse {

    private String chartTitle;
    private List<String> labels;
    private List<Long> data;

    /**
     * Optional secondary dataset (e.g. for stacked/grouped bar charts
     * like overtime: "Left" vs "Stayed").
     */
    private Map<String, List<Long>> datasets;
}
