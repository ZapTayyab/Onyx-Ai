from __future__ import annotations

from app.services.persona_generator import PersonaCategory, PersonaGenerator, PersonaProfile


class TestPersonaGenerator:
    def setup_method(self) -> None:
        self.generator = PersonaGenerator()

    def test_builtin_profiles_returns_list(self) -> None:
        profiles = self.generator.get_builtin_profiles()
        assert len(profiles) >= 5
        assert all(isinstance(p, PersonaProfile) for p in profiles)

    def test_builtin_profiles_filtered_by_category(self) -> None:
        adversarial = self.generator.get_builtin_profiles(categories=[PersonaCategory.ADVERSARIAL])
        assert all(p.category == PersonaCategory.ADVERSARIAL for p in adversarial)
        assert len(adversarial) >= 2

        standard = self.generator.get_builtin_profiles(categories=[PersonaCategory.STANDARD])
        assert all(p.category == PersonaCategory.STANDARD for p in standard)

    def test_builtin_profiles_filtered_multiple_categories(self) -> None:
        filtered = self.generator.get_builtin_profiles(
            categories=[PersonaCategory.STANDARD, PersonaCategory.EDGE_CASE]
        )
        categories = {p.category for p in filtered}
        assert PersonaCategory.ADVERSARIAL not in categories
        assert len(filtered) >= 3

    def test_profile_has_required_fields(self) -> None:
        profile = self.generator.get_builtin_profiles()[0]
        assert profile.name
        assert profile.category in PersonaCategory
        assert 0.0 <= profile.digital_literacy_score <= 1.0
        assert isinstance(profile.edge_case_triggers, list)

    def test_generate_conversation_script_returns_turns(self) -> None:
        profile = self.generator.get_builtin_profiles()[0]
        script = self.generator.generate_conversation_script(profile, max_turns=5)
        assert len(script) == 5
        assert all(isinstance(turn, str) and len(turn) > 0 for turn in script)

    def test_conversation_script_starts_with_intent(self) -> None:
        profile = self.generator.get_builtin_profiles()[0]
        script = self.generator.generate_conversation_script(profile)
        opening = script[0].lower()
        intent_words = profile.initial_user_intent.lower().split()[:3]
        assert any(word in opening for word in intent_words)

    def test_standard_persona_has_high_literacy(self) -> None:
        standard = self.generator.get_builtin_profiles(categories=[PersonaCategory.STANDARD])
        for p in standard:
            assert p.digital_literacy_score >= 0.6

    def test_edge_case_persona_has_low_literacy(self) -> None:
        edge = self.generator.get_builtin_profiles(categories=[PersonaCategory.EDGE_CASE])
        for p in edge:
            assert p.digital_literacy_score <= 0.4

    def test_adversarial_persona_has_injection_triggers(self) -> None:
        adversarial = self.generator.get_builtin_profiles(categories=[PersonaCategory.ADVERSARIAL])
        for p in adversarial:
            assert len(p.edge_case_triggers) >= 3
            has_security_trigger = any(
                "ignore" in t.lower() or "select" in t.lower() or "prompt" in t.lower() or "emergency" in t.lower()
                for t in p.edge_case_triggers
            )
            assert has_security_trigger, f"{p.name} lacks security triggers"

    def test_generate_persona_without_llm_returns_template(self) -> None:
        profile = self.generator._get_template_persona(PersonaCategory.STANDARD)
        assert profile.name == "Template Persona"
        assert profile.category == PersonaCategory.STANDARD

    def test_build_synthesis_prompt_includes_system_prompt(self) -> None:
        prompt = self.generator._build_synthesis_prompt(
            "You are a helpful assistant.", PersonaCategory.ADVERSARIAL
        )
        assert "You are a helpful assistant" in prompt
        assert "adversarial" in prompt
        assert "JSON" in prompt or "json" in prompt
