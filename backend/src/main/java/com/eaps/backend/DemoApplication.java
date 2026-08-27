package com.eaps.backend;

import com.eaps.backend.model.AppUser;
import com.eaps.backend.repository.AppUserRepository;
import org.springframework.boot.CommandLineRunner;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.context.annotation.Bean;
import org.springframework.security.crypto.password.PasswordEncoder;
import java.util.Optional;

@SpringBootApplication
public class DemoApplication {

	public static void main(String[] args) {
		SpringApplication.run(DemoApplication.class, args);
	}

	@Bean
	CommandLineRunner updateAdminPassword(AppUserRepository userRepository, PasswordEncoder passwordEncoder) {
		return args -> {
			Optional<AppUser> adminOpt = userRepository.findByEmail("admin@company.com");
			if (adminOpt.isPresent()) {
				AppUser admin = adminOpt.get();
				// If it's still using the placeholder hash, update it
				if (admin.getPassword().startsWith("$2a$10$REPLACE_WITH_REAL_BCRYPT_HASH")) {
					admin.setPassword(passwordEncoder.encode("Admin@123"));
					userRepository.save(admin);
					System.out.println("✅ Admin password updated successfully to 'Admin@123'");
				}
			}
		};
	}
}
