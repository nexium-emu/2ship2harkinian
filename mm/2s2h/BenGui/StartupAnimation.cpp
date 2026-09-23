#include "StartupAnimation.h"

#include "BenPort.h"
#include <fast/Fast3dGui.h>
#include <fast/Fast3dWindow.h>
#include <ship/config/ConsoleVariable.h>
#include <ship/resource/archive/ArchiveManager.h>
#include <imgui.h>
#include <algorithm>
#include <chrono>
#include <cfloat>
#include <cmath>
#include <cstring>
#include <thread>

#ifdef __APPLE__
#include <SDL_gamecontroller.h>
#else
#include <SDL2/SDL_gamecontroller.h>
#endif

namespace BenGui {
namespace {
constexpr float PI = 3.141592654f;
constexpr float DURATION = 4.2f;
constexpr const char* SHIP_TEXTURE = "StartupShip";
constexpr const char* SHIP_PATH = "textures/icons/g2ShipIcon.png";

float Ease(float value) {
    value = std::clamp(value, 0.0f, 1.0f);
    return value * value * (3.0f - 2.0f * value);
}

ImU32 Color(int red, int green, int blue, float alpha = 1.0f) {
    return IM_COL32(red, green, blue, static_cast<int>(255.0f * std::clamp(alpha, 0.0f, 1.0f)));
}

void CenteredText(ImDrawList* draw, ImFont* font, float size, ImVec2 position, ImU32 color, const char* text,
                  float spacing = 0.0f) {
    const size_t length = std::strlen(text);
    float width = font->CalcTextSizeA(size, FLT_MAX, 0.0f, text).x;
    width += spacing * static_cast<float>(length > 0 ? length - 1 : 0);
    position.x -= width * 0.5f;
    for (size_t i = 0; i < length; ++i) {
        draw->AddText(font, size, position, color, text + i, text + i + 1);
        position.x += font->CalcTextSizeA(size, FLT_MAX, 0.0f, text + i, text + i + 1).x + spacing;
    }
}

void DrawIntroduction(float time, float opacity, ImTextureID ship) {
    const auto viewport = ImGui::GetMainViewport();
    auto draw = ImGui::GetForegroundDrawList(viewport);
    const ImVec2 origin = viewport->Pos;
    const ImVec2 size = viewport->Size;
    const float scale = std::min(size.x / 1280.0f, size.y / 720.0f);
    const float centerX = origin.x + size.x * 0.5f;
    auto point = [&](float x, float y) { return ImVec2(centerX + x * scale, origin.y + size.y * 0.5f + y * scale); };
    auto font = OTRGlobals::Instance->fontStandardLargest;
    if (font == nullptr) {
        font = ImGui::GetFont();
    }
    auto titleFont = OTRGlobals::Instance->fontStartupTitle;
    if (titleFont == nullptr) {
        titleFont = font;
    }

    draw->PushClipRect(origin, ImVec2(origin.x + size.x, origin.y + size.y), true);
    draw->AddRectFilled(origin, ImVec2(origin.x + size.x, origin.y + size.y), IM_COL32(0, 0, 0, 255));
    draw->AddRectFilledMultiColor(origin, ImVec2(origin.x + size.x, origin.y + size.y), Color(16, 10, 29, opacity),
                                  Color(16, 10, 29, opacity), Color(5, 19, 26, opacity), Color(5, 19, 26, opacity));

    const ImVec2 emblem = point(0.0f, -95.0f);
    const float reveal = Ease(time / 0.9f);
    // Soft amethyst light behind the clock and the original pixel-art ship.
    for (int i = 14; i > 0; --i) {
        draw->AddCircleFilled(emblem, (82.0f + i * 9.0f) * scale, Color(98, 53, 146, 0.015f * opacity * reveal), 80);
    }
    for (int i = 0; i < 28; ++i) {
        const float x = std::sin(i * 7.13f) * 555.0f;
        const float y = std::cos(i * 2.71f) * 290.0f - time * (2.0f + i % 3);
        const float light = (0.18f + 0.14f * std::sin(time * 1.4f + i)) * opacity;
        draw->AddCircleFilled(point(x, y), (i % 4 == 0 ? 1.5f : 0.8f) * scale, Color(228, 208, 159, light));
    }

    const float radius = (103.0f + 9.0f * (1.0f - reveal)) * scale;
    draw->AddCircle(emblem, radius, Color(203, 165, 91, 0.38f * opacity * reveal), 96, scale);
    draw->AddCircle(emblem, radius - 6.0f * scale, Color(185, 151, 219, 0.16f * opacity * reveal), 96, scale);
    for (int i = 0; i < 48; ++i) {
        const float angle = i * PI / 24.0f - PI * 0.5f;
        const float outer = radius + (i % 4 == 0 ? 9.0f : 4.0f) * scale;
        draw->AddLine(ImVec2(emblem.x + std::cos(angle) * radius, emblem.y + std::sin(angle) * radius),
                      ImVec2(emblem.x + std::cos(angle) * outer, emblem.y + std::sin(angle) * outer),
                      Color(219, 189, 124, (i % 4 == 0 ? 0.58f : 0.20f) * opacity * reveal), scale);
    }
    draw->PathArcTo(emblem, radius + 17.0f * scale, -PI * 0.5f + time * 0.18f,
                    -PI * 0.5f + time * 0.18f + reveal * PI * 1.35f, 64);
    draw->PathStroke(Color(178, 132, 226, 0.48f * opacity), 0, 2.0f * scale);

    if (ship != nullptr) {
        const float half = (64.0f + 5.0f * reveal) * scale;
        const float bob = std::sin(time * 1.5f) * 3.0f * scale + (1.0f - reveal) * 15.0f * scale;
        draw->AddImage(ship, ImVec2(emblem.x - half, emblem.y - half + bob),
                       ImVec2(emblem.x + half, emblem.y + half + bob), ImVec2(0, 0), ImVec2(1, 1),
                       Color(255, 255, 255, opacity * reveal));
    }

    // Quiet waves connect the nautical emblem to the continuation credit.
    for (int row = 0; row < 3; ++row) {
        for (int i = 0; i <= 80; ++i) {
            const float x = -240.0f + i * 6.0f;
            const float taper = std::max(0.0f, 1.0f - std::abs(x) / 240.0f);
            draw->PathLineTo(point(x, 41.0f + row * 7.0f + std::sin(x * 0.018f + time + row) * 3.0f * taper));
        }
        draw->PathStroke(Color(118, 160, 180, (0.22f - row * 0.05f) * opacity * reveal), 0, scale);
    }

    CenteredText(draw, font, 14.0f * scale, point(0, -264), Color(219, 190, 136, opacity * reveal),
                 "2 SHIP 2 HARKINIAN", 3.0f * scale);
    const float creditReveal = Ease((time - 0.45f) / 0.65f);
    CenteredText(draw, font, 23.0f * scale, point(0, 86.0f + 8.0f * (1.0f - creditReveal)),
                 Color(184, 169, 208, opacity * creditReveal), "Continued By", 1.4f * scale);
    const float nameReveal = Ease((time - 0.85f) / 0.75f);
    const ImVec2 namePosition = point(0, 122.0f + 12.0f * (1.0f - nameReveal));
    CenteredText(draw, titleFont, 72.0f * scale, ImVec2(namePosition.x, namePosition.y + 3.0f * scale),
                 Color(77, 40, 111, opacity * nameReveal), "Mythrax", 2.0f * scale);
    CenteredText(draw, titleFont, 72.0f * scale, namePosition, Color(240, 220, 173, opacity * nameReveal), "Mythrax",
                 2.0f * scale);
    const float lineWidth = 150.0f * nameReveal;
    draw->AddLine(point(-lineWidth, 222), point(lineWidth, 222), Color(193, 150, 88, 0.45f * opacity * nameReveal),
                  scale);
    draw->AddQuadFilled(point(0, 217), point(5, 222), point(0, 227), point(-5, 222),
                        Color(229, 199, 136, opacity * nameReveal));
    CenteredText(draw, font, 12.0f * scale, point(0, 307), Color(156, 146, 170, opacity * Ease(time - 1.4f)),
                 "ENTER / CLICK TO CONTINUE", 1.3f * scale);
    draw->PopClipRect();
}

bool ControllerSkipDown() {
    // Use already-open controllers; the game's OSContPad buffer does not exist yet.
    for (int i = 0; i < SDL_NumJoysticks(); ++i) {
        auto controller = SDL_GameControllerFromInstanceID(SDL_JoystickGetDeviceInstanceID(i));
        if (controller != nullptr && (SDL_GameControllerGetButton(controller, SDL_CONTROLLER_BUTTON_A) ||
                                      SDL_GameControllerGetButton(controller, SDL_CONTROLLER_BUTTON_B) ||
                                      SDL_GameControllerGetButton(controller, SDL_CONTROLLER_BUTTON_START))) {
            return true;
        }
    }
    return false;
}
} // namespace

bool RunStartupAnimation() {
    auto window = std::dynamic_pointer_cast<Fast::Fast3dWindow>(Ship::Context::GetRawInstance()->GetWindow());
    auto gui = std::dynamic_pointer_cast<Fast::Fast3dGui>(window->GetGui());
    if (Ship::Context::GetRawInstance()->GetResourceManager()->GetArchiveManager()->HasFile(SHIP_PATH)) {
        gui->LoadTextureFromRawImage(SHIP_TEXTURE, SHIP_PATH);
    }
    auto ship = gui->GetTextureByName(SHIP_TEXTURE);

    // The saved menu may be open, but its game-dependent entries are not initialized yet.
    // Detach it temporarily without changing its visibility or any saved settings.
    auto menu = gui->GetMenu();
    gui->SetMenu(nullptr);
    std::vector<std::shared_ptr<Ship::GuiWindow>> hiddenWindows;
    const std::pair<const char*, const char*> startupWindows[] = {
        { "2S2H Input Editor", "gWindows.BenInputEditor" },
        { "Console", CVAR_CONSOLE_WINDOW_OPEN },
        { "Stats", CVAR_STATS_WINDOW_OPEN },
    };
    auto cvars = Ship::Context::GetRawInstance()->GetConsoleVariables();
    for (const auto& [name, visibilityCvar] : startupWindows) {
        auto guiWindow = gui->GetGuiWindow(name);
        if (guiWindow != nullptr && guiWindow->IsVisible()) {
            hiddenWindows.push_back(guiWindow);
            const int visibility = cvars->GetInteger(visibilityCvar, 1);
            guiWindow->Hide();
            // Hide synchronizes the CVar; restore it before any frame can save settings.
            cvars->SetInteger(visibilityCvar, visibility);
        }
    }
    using Clock = std::chrono::steady_clock;
    Clock::time_point start;
    bool started = false;
    bool previousControllerDown = ControllerSkipDown();
    float skipTime = -1.0f;
    while (window->IsRunning()) {
        window->HandleEvents();
        if (!window->IsRunning()) {
            break;
        }
        if (!window->IsFrameReady()) {
            std::this_thread::sleep_for(std::chrono::milliseconds(1));
            continue;
        }
        gui->StartDraw();
        window->StartFrame();
        window->RunGuiOnly();
        if (!started) {
            start = Clock::now();
            started = true;
        }
        const float elapsed = std::chrono::duration<float>(Clock::now() - start).count();
        const bool controllerDown = ControllerSkipDown();
        const bool skipPressed = ImGui::IsKeyPressed(ImGuiKey_Enter, false) ||
                                 ImGui::IsKeyPressed(ImGuiKey_Space, false) || ImGui::IsMouseClicked(0) ||
                                 (controllerDown && !previousControllerDown);
        previousControllerDown = controllerDown;
        if (skipPressed && skipTime < 0.0f) {
            skipTime = elapsed;
        }
        float opacity = Ease(elapsed / 0.55f) * (1.0f - Ease((elapsed - (DURATION - 0.65f)) / 0.65f));
        if (skipTime >= 0.0f) {
            opacity *= 1.0f - Ease((elapsed - skipTime) / 0.2f);
        }
        DrawIntroduction(elapsed, opacity, ship);
        gui->EndDraw();
        window->EndFrame();
        if (elapsed >= DURATION || (skipTime >= 0.0f && elapsed >= skipTime + 0.2f)) {
            break;
        }
    }
    gui->SetMenu(menu);
    for (const auto& guiWindow : hiddenWindows) {
        guiWindow->Show();
    }
    window->GetMouseStateManager()->UpdateMouseCapture();
    gui->UnloadTexture(SHIP_TEXTURE);
    return window->IsRunning();
}
} // namespace BenGui
