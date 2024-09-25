from pygame.key import ScancodeWrapper

from models.Entity import Entity


class SkillSystem:
    def use_skills(self, keys: ScancodeWrapper, mouse_position: tuple[int, int]):
        for entity in Entity.entity_group:
            preferred_skills = entity.get_preferred_skills(keys, mouse_position)

            for skill in preferred_skills:
                skill.spawn_projectiles()

        for entity in Entity.entity_group:
            entity.age()
