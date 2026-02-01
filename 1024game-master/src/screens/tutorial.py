import pygame
from typing import Callable
from ..config import SCREEN_WIDTH, SCREEN_HEIGHT, TEXT_COLOR, BG_COLOR, PRIMARY_COLOR, SECONDARY_COLOR, ACCENT_COLOR
from ..ui import Button, get_font


class TutorialScreen:
    def __init__(self, screen: pygame.Surface, on_back: Callable):
        self.screen = screen
        self.on_back = on_back
        
        self.title_font = get_font(64)
        self.heading_font = get_font(42)
        self.text_font = get_font(28)
        self.small_font = get_font(24)
        
        self.back_button = Button(
            screen, 50, SCREEN_HEIGHT - 80, 120, 50,
            "返回", self.on_back,
            color=SECONDARY_COLOR, text_color=TEXT_COLOR
        )
        
        self.scroll_offset = 0
        
        self.sections = [
            {
                "title": "游戏目标",
                "content": "在网格中滑动方块，合并相同数字的方块，达到目标值！\n\n"
                          "经典模式: 达到 2048\n"
                          "关卡模式: 达到各关卡指定的目标值"
            },
            {
                "title": "基本操作",
                "content": "↑ ↓ ← → 或 W A S D: 移动方块\n"
                          "鼠标拖动: 滑动方块\n"
                          "ESC: 暂停游戏\n"
                          "R: 重新开始当前关卡"
            },
            {
                "title": "合并规则",
                "content": "• 相同数字的方块相邻时会合并\n"
                          "• 合并后数字翻倍 (2 + 2 = 4, 4 + 4 = 8...)\n"
                          "• 每次移动后随机生成新方块\n"
                          "• 无法移动时游戏结束"
            },
            {
                "title": "得分系统",
                "content": "• 合并方块获得分数\n"
                          "• 合并数字越大，得分越高\n"
                          "• 连续合并可获得连击加成\n"
                          "• 完成时间越短，星级越高"
            },
            {
                "title": "难度等级",
                "content": "🟢 简单 (关卡 1-5): 4x4 网格，时间充裕\n"
                          "🟡 中等 (关卡 6-10): 5x5 网格，难度适中\n"
                          "🟠 困难 (关卡 11-15): 6x6 网格，挑战极限\n"
                          "🔴 专家 (关卡 16-20): 7x7 网格，终极考验"
            },
            {
                "title": "成就系统",
                "content": "完成特定目标可解锁成就：\n"
                          "• 首次胜利\n"
                          "• 60秒内完成关卡\n"
                          "• 达到高分\n"
                          "• 完成所有关卡\n"
                          "• 获得三星评价"
            },
            {
                "title": "小技巧",
                "content": "💡 保持最大数字在角落\n"
                          "💡 有序排列方块\n"
                          "💡 避免随机方块打乱布局\n"
                          "💡 预判下一步移动"
            }
        ]
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 4:
                self.scroll_offset = min(0, self.scroll_offset + 40)
            elif event.button == 5:
                self.scroll_offset = max(-300, self.scroll_offset - 40)
        
        if self.back_button.handle_event(event):
            return True
        
        return False
    
    def update(self, dt: float):
        self.back_button.update()
    
    def draw(self):
        self.screen.fill(BG_COLOR)
        
        title = self.title_font.render("游戏教程", True, ACCENT_COLOR)
        self.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 50))
        
        y = 130 + self.scroll_offset
        section_spacing = 20
        
        for section in self.sections:
            heading = self.heading_font.render(section["title"], True, PRIMARY_COLOR)
            self.screen.blit(heading, (100, y))
            y += heading.get_height() + 10
            
            lines = section["content"].split("\n")
            for line in lines:
                text = self.small_font.render(line, True, TEXT_COLOR)
                self.screen.blit(text, (100, y))
                y += text.get_height() + 3
            
            y += section_spacing
        
        self.back_button.draw()
